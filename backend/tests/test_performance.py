"""
6.3.1 响应时间与并发处理测试
测试接口性能、推荐算法性能、并发处理能力
"""
import requests
import json
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class PerformanceTester:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.test_results = []

    def log_result(self, test_name, passed, message='', details=None):
        """记录测试结果"""
        result = {
            'test_name': test_name,
            'passed': passed,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = '✓ PASS' if passed else '✗ FAIL'
        print(f"{status} | {test_name}: {message}")
        if details:
            print(f"  详情: {json.dumps(details, ensure_ascii=False, indent=2)}")
        return passed

    def login(self, identifier='admin', password='admin123'):
        """用户登录"""
        try:
            response = requests.post(
                f'{self.base_url}/api/auth/login',
                json={'username': identifier, 'password': password}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.user_id = data.get('user', {}).get('id')
                return self.log_result(
                    'TC-PERF-000: 用户登录',
                    True,
                    f'登录成功，用户ID: {self.user_id}'
                )
            else:
                return self.log_result(
                    'TC-PERF-000: 用户登录',
                    False,
                    f'登录失败: {response.status_code}'
                )
        except Exception as e:
            return self.log_result('TC-PERF-000: 用户登录', False, f'异常: {str(e)}')

    def get_headers(self):
        """获取请求头"""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def test_login_response_time(self):
        """TC-PERF-001: 测试登录接口响应时间"""
        try:
            times = []
            for i in range(10):
                start_time = time.time()
                response = requests.post(
                    f'{self.base_url}/api/auth/login',
                    json={'username': 'testuser1', 'password': 'password123'}
                )
                elapsed = (time.time() - start_time) * 1000
                if response.status_code == 200:
                    times.append(elapsed)

            if not times:
                return self.log_result(
                    'TC-PERF-001: 登录响应时间',
                    False,
                    '所有登录请求失败'
                )

            avg_time = sum(times) / len(times)
            p95_time = sorted(times)[int(len(times) * 0.95)]

            # 期望平均响应时间 < 100ms, 95%响应时间 < 150ms
            passed = avg_time < 100 and p95_time < 150

            return self.log_result(
                'TC-PERF-001: 登录响应时间',
                passed,
                f'平均: {avg_time:.0f}ms, 95%: {p95_time:.0f}ms',
                {
                    'average_ms': round(avg_time, 2),
                    'p95_ms': round(p95_time, 2),
                    'min_ms': round(min(times), 2),
                    'max_ms': round(max(times), 2)
                }
            )
        except Exception as e:
            return self.log_result('TC-PERF-001: 登录响应时间', False, f'异常: {str(e)}')

    def test_item_list_response_time(self):
        """TC-PERF-002: 测试商品列表响应时间"""
        try:
            times = []
            for i in range(10):
                start_time = time.time()
                response = requests.get(
                    f'{self.base_url}/api/items',
                    headers=self.get_headers(),
                    params={'page': 1, 'per_page': 20}
                )
                elapsed = (time.time() - start_time) * 1000
                if response.status_code == 200:
                    times.append(elapsed)

            if not times:
                return self.log_result(
                    'TC-PERF-002: 商品列表响应时间',
                    False,
                    '所有请求失败'
                )

            avg_time = sum(times) / len(times)
            p95_time = sorted(times)[int(len(times) * 0.95)]

            # 期望平均响应时间 < 150ms, 95%响应时间 < 200ms
            passed = avg_time < 150 and p95_time < 200

            return self.log_result(
                'TC-PERF-002: 商品列表响应时间',
                passed,
                f'平均: {avg_time:.0f}ms, 95%: {p95_time:.0f}ms',
                {
                    'average_ms': round(avg_time, 2),
                    'p95_ms': round(p95_time, 2),
                    'threshold_met': passed
                }
            )
        except Exception as e:
            return self.log_result('TC-PERF-002: 商品列表响应时间', False, f'异常: {str(e)}')

    def test_recommendation_response_time(self):
        """TC-PERF-003: 测试推荐接口响应时间"""
        try:
            times = []
            for i in range(10):
                start_time = time.time()
                response = requests.get(
                    f'{self.base_url}/api/recommendations/personal',
                    headers=self.get_headers()
                )
                elapsed = (time.time() - start_time) * 1000
                if response.status_code == 200:
                    times.append(elapsed)

            if not times:
                return self.log_result(
                    'TC-PERF-003: 推荐响应时间',
                    False,
                    '所有请求失败'
                )

            avg_time = sum(times) / len(times)
            p95_time = sorted(times)[int(len(times) * 0.95)]

            # 期望平均响应时间 < 250ms, 95%响应时间 < 400ms
            passed = avg_time < 250 and p95_time < 400

            return self.log_result(
                'TC-PERF-003: 推荐响应时间',
                passed,
                f'平均: {avg_time:.0f}ms, 95%: {p95_time:.0f}ms',
                {
                    'average_ms': round(avg_time, 2),
                    'p95_ms': round(p95_time, 2),
                    'threshold_met': passed
                }
            )
        except Exception as e:
            return self.log_result('TC-PERF-003: 推荐响应时间', False, f'异常: {str(e)}')

    def test_concurrent_requests(self):
        """TC-PERF-004: 测试并发请求处理"""
        try:
            concurrent_users = 50
            success_count = 0
            error_count = 0
            times = []

            def make_request():
                try:
                    start_time = time.time()
                    response = requests.get(
                        f'{self.base_url}/api/items',
                        headers=self.get_headers(),
                        timeout=10
                    )
                    elapsed = (time.time() - start_time) * 1000
                    return response.status_code == 200, elapsed
                except Exception:
                    return False, 0

            with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = [executor.submit(make_request) for _ in range(concurrent_users)]

                for future in as_completed(futures):
                    success, elapsed = future.result()
                    if success:
                        success_count += 1
                        times.append(elapsed)
                    else:
                        error_count += 1

            success_rate = (success_count / concurrent_users) * 100
            avg_time = sum(times) / len(times) if times else 0

            # 期望成功率 > 95%, 平均响应时间 < 500ms
            passed = success_rate >= 95 and avg_time < 500

            return self.log_result(
                'TC-PERF-004: 并发请求处理',
                passed,
                f'成功率: {success_rate:.1f}%, 平均响应: {avg_time:.0f}ms',
                {
                    'concurrent_users': concurrent_users,
                    'success_count': success_count,
                    'error_count': error_count,
                    'success_rate': f'{success_rate:.1f}%',
                    'average_response_ms': round(avg_time, 2)
                }
            )
        except Exception as e:
            return self.log_result('TC-PERF-004: 并发请求处理', False, f'异常: {str(e)}')

    def test_search_performance(self):
        """TC-PERF-005: 测试搜索性能"""
        try:
            search_keywords = ['手机', '电脑', '书籍', '自行车', '衣服']
            times = []

            for keyword in search_keywords:
                start_time = time.time()
                response = requests.get(
                    f'{self.base_url}/api/items/search',
                    headers=self.get_headers(),
                    params={'keyword': keyword}
                )
                elapsed = (time.time() - start_time) * 1000
                if response.status_code == 200:
                    times.append(elapsed)

            if not times:
                return self.log_result(
                    'TC-PERF-005: 搜索性能',
                    False,
                    '所有搜索请求失败'
                )

            avg_time = sum(times) / len(times)
            max_time = max(times)

            # 期望平均响应时间 < 150ms, 最大响应时间 < 300ms
            passed = avg_time < 150 and max_time < 300

            return self.log_result(
                'TC-PERF-005: 搜索性能',
                passed,
                f'平均: {avg_time:.0f}ms, 最大: {max_time:.0f}ms',
                {
                    'average_ms': round(avg_time, 2),
                    'max_ms': round(max_time, 2),
                    'search_count': len(times)
                }
            )
        except Exception as e:
            return self.log_result('TC-PERF-005: 搜索性能', False, f'异常: {str(e)}')

    def test_database_query_performance(self):
        """TC-PERF-006: 测试数据库查询性能"""
        try:
            # 测试不同类型的查询
            queries = [
                ('商品列表', '/api/items', {'page': 1, 'per_page': 20}),
                ('商品详情', '/api/items/1', None),
                ('用户信息', '/api/users/me', None),
                ('类目列表', '/api/categories', None)
            ]

            results = []
            all_fast = True

            for name, endpoint, params in queries:
                start_time = time.time()
                response = requests.get(
                    f'{self.base_url}{endpoint}',
                    headers=self.get_headers(),
                    params=params
                )
                elapsed = (time.time() - start_time) * 1000

                is_fast = elapsed < 100  # 100ms阈值
                all_fast = all_fast and is_fast

                results.append({
                    'query': name,
                    'response_time_ms': round(elapsed, 2),
                    'is_fast': is_fast
                })

            return self.log_result(
                'TC-PERF-006: 数据库查询性能',
                all_fast,
                '所有查询性能正常' if all_fast else '部分查询较慢',
                {'queries': results}
            )
        except Exception as e:
            return self.log_result('TC-PERF-006: 数据库查询性能', False, f'异常: {str(e)}')

    def test_cache_effectiveness(self):
        """TC-PERF-007: 测试缓存有效性"""
        try:
            # 第一次请求（冷启动）
            start_time1 = time.time()
            response1 = requests.get(
                f'{self.base_url}/api/recommendations/hot',
                headers=self.get_headers(),
                params={'limit': 29}
            )
            time1 = (time.time() - start_time1) * 1000

            if response1.status_code != 200:
                return self.log_result(
                    'TC-PERF-007: 缓存有效性',
                    False,
                    '第一次请求失败'
                )

            # 第二次请求（应该命中缓存）
            start_time2 = time.time()
            response2 = requests.get(
                f'{self.base_url}/api/recommendations/hot',
                headers=self.get_headers(),
                params={'limit': 29}
            )
            time2 = (time.time() - start_time2) * 1000

            if response2.status_code != 200:
                return self.log_result(
                    'TC-PERF-007: 缓存有效性',
                    False,
                    '第二次请求失败'
                )

            # 缓存应该使第二次请求更快
            speedup = time1 / time2 if time2 > 0 else 1
            cache_effective = speedup > 1.2  # 至少快20%

            return self.log_result(
                'TC-PERF-007: 缓存有效性',
                cache_effective,
                f'加速比: {speedup:.2f}x',
                {
                    'first_request_ms': round(time1, 2),
                    'second_request_ms': round(time2, 2),
                    'speedup': f'{speedup:.2f}x',
                    'cache_effective': cache_effective
                }
            )
        except Exception as e:
            return self.log_result('TC-PERF-007: 缓存有效性', False, f'异常: {str(e)}')

    def run_all_tests(self):
        """运行所有性能测试"""
        print("\n" + "="*80)
        print("开始执行 6.3.1 响应时间与并发处理测试")
        print("="*80 + "\n")

        # 登录
        if not self.login():
            print("\n登录失败，无法继续测试")
            return self.generate_report()

        print()

        # 执行所有测试
        self.test_login_response_time()
        self.test_item_list_response_time()
        self.test_recommendation_response_time()
        self.test_concurrent_requests()
        self.test_search_performance()
        self.test_database_query_performance()
        self.test_cache_effectiveness()

        return self.generate_report()

    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*80)
        print("测试报告")
        print("="*80)

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0

        print(f"\n总计: {total} 个测试")
        print(f"通过: {passed} 个")
        print(f"失败: {failed} 个")
        print(f"通过率: {pass_rate:.1f}%")

        if failed > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test_name']}: {result['message']}")

        print("\n" + "="*80 + "\n")

        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': pass_rate,
            'results': self.test_results
        }

if __name__ == '__main__':
    tester = PerformanceTester()
    report = tester.run_all_tests()

    # 保存测试报告
    with open('test_report_performance.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"测试报告已保存到: test_report_performance.json")
