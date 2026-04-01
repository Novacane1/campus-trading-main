"""
时空匹配服务验证脚本
"""
import os
import sys
import importlib.util

ROOT = os.path.join(os.path.dirname(__file__), '..')
MODULE_PATH = os.path.join(ROOT, 'app', 'services', 'time_location.py')
spec = importlib.util.spec_from_file_location('time_location_service', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
TimeLocationService = module.TimeLocationService


PASS = 0
FAIL = 0


def report(ok, name, detail=''):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f'  [PASS] {name}')
    else:
        FAIL += 1
        print(f'  [FAIL] {name}: {detail}')


def test_exact_match():
    result = TimeLocationService.get_match_suggestions(
        buyer_time_slots=['周三 14:00-18:00'],
        buyer_locations=['主图书馆门口'],
        seller_time_slots=['周三 16:00-20:00'],
        seller_locations=['图书馆']
    )
    report(result['best_time_slot'] == '周三 16:00-18:00', '精确时间重叠')
    report(result['best_location'] == '图书馆', '地点别名归一化')
    report(result['match_score'] >= 80, '精确匹配高分', str(result))


def test_negotiation_time():
    result = TimeLocationService.get_match_suggestions(
        buyer_time_slots=['周四 14:00-18:00'],
        buyer_locations=['食堂'],
        seller_time_slots=['周四 19:00-21:00'],
        seller_locations=['食堂门口']
    )
    report(result['best_time_slot'] is None, '无精确重叠时不返回 exact time')
    report(
        bool(result['best_time_label']) and '周四' in result['best_time_label'],
        '生成协商时间建议',
        str(result.get('best_time_label'))
    )
    report(result['best_location'] == '食堂', '地点折叠到统一候选')


def test_missing_buyer_preferences():
    result = TimeLocationService.get_match_suggestions(
        buyer_time_slots=[],
        buyer_locations=[],
        seller_time_slots=['周五 10:00-12:00'],
        seller_locations=['校门']
    )
    report(result['buyer_missing_time_preferences'] is True, '识别缺少时间偏好')
    report(result['buyer_missing_location_preferences'] is True, '识别缺少地点偏好')
    report(
        '补充常用交易时间后' in ' '.join(result['profile_completion_tips']),
        '返回完善偏好提示'
    )
    report(result['best_location'] == '校门口', '单边地点也能给出公共地点建议')


def test_public_compromise_location():
    result = TimeLocationService.get_match_suggestions(
        buyer_time_slots=['周六 10:00-12:00'],
        buyer_locations=['教学楼'],
        seller_time_slots=['周六 10:00-12:00'],
        seller_locations=['图书馆']
    )
    report(bool(result['location_candidates']), '生成地点候选')
    report(result['best_location'] in {'教学楼', '图书馆'}, '返回最优地点候选', str(result.get('best_location')))
    report(result['has_match'] is True, '有可执行方案')


def main():
    print('=' * 56)
    print('  时空匹配服务验证')
    print('=' * 56)
    test_exact_match()
    test_negotiation_time()
    test_missing_buyer_preferences()
    test_public_compromise_location()
    print('=' * 56)
    print(f'  测试汇总: PASS={PASS} FAIL={FAIL}')
    print('=' * 56)
    raise SystemExit(1 if FAIL else 0)


if __name__ == '__main__':
    main()
