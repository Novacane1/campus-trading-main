"""
6.2.1 核心推荐功能测试
测试个性化推荐、相似商品推荐、价格建议等功能
"""
import requests
import json
import time
from datetime import datetime

class RecommendationTester:
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
        """用户登录获取Token"""
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
                    'TC-REC-000: 用户登录',
                    True,
                    f'登录成功，用户ID: {self.user_id}',
                    {'token_length': len(self.token) if self.token else 0}
                )
            else:
                return self.log_result(
                    'TC-REC-000: 用户登录',
                    False,
                    f'登录失败: {response.status_code}',
                    response.json()
                )
        except Exception as e:
            return self.log_result('TC-REC-000: 用户登录', False, f'异常: {str(e)}')

    def get_headers(self):
        """获取请求头"""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def test_personal_recommendation(self):
        """TC-REC-001: 测试个性化推荐"""
        try:
            response = requests.get(
                f'{self.base_url}/api/recommendations/personal',
                headers=self.get_headers()
            )

            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])

                # 验证返回数据结构
                if not isinstance(items, list):
                    return self.log_result(
                        'TC-REC-001: 个性化推荐',
                        False,
                        '返回数据格式错误，items不是列表'
                    )

                # 验证推荐数量
                if len(items) == 0:
                    return self.log_result(
                        'TC-REC-001: 个性化推荐',
                        False,
                        '推荐结果为空'
                    )

                # 验证推荐商品字段完整性
                required_fields = ['id', 'name', 'price', 'category_id']
                for item in items[:3]:  # 检查前3个商品
                    missing_fields = [f for f in required_fields if f not in item]
                    if missing_fields:
                        return self.log_result(
                            'TC-REC-001: 个性化推荐',
                            False,
                            f'商品字段不完整，缺少: {missing_fields}',
                            item
                        )

                return self.log_result(
                    'TC-REC-001: 个性化推荐',
                    True,
                    f'成功获取{len(items)}个推荐商品',
                    {
                        'count': len(items),
                        'sample_items': [
                            {'id': i['id'], 'name': i['name'], 'price': str(i['price'])}
                            for i in items[:3]
                        ]
                    }
                )
            else:
                return self.log_result(
                    'TC-REC-001: 个性化推荐',
                    False,
                    f'请求失败: {response.status_code}',
                    response.json()
                )
        except Exception as e:
            return self.log_result('TC-REC-001: 个性化推荐', False, f'异常: {str(e)}')

    def test_similar_items(self, item_id=None):
        """TC-REC-002: 测试相似商品推荐"""
        try:
            # 如果没有指定商品ID，先获取一个商品
            if not item_id:
                response = requests.get(
                    f'{self.base_url}/api/items',
                    headers=self.get_headers(),
                    params={'page': 1, 'per_page': 1}
                )
                if response.status_code == 200:
                    items = response.json().get('items', [])
                    if items:
                        item_id = items[0]['id']
                    else:
                        return self.log_result(
                            'TC-REC-002: 相似商品推荐',
                            False,
                            '无法获取测试商品'
                        )

            # 测试相似商品推荐
            response = requests.get(
                f'{self.base_url}/api/recommendations/similar/{item_id}',
                headers=self.get_headers()
            )

            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])

                if len(items) == 0:
                    return self.log_result(
                        'TC-REC-002: 相似商品推荐',
                        True,  # 可能确实没有相似商品
                        f'商品{item_id}暂无相似商品'
                    )

                # 验证相似商品不包含原商品
                similar_ids = [i['id'] for i in items]
                if item_id in similar_ids:
                    return self.log_result(
                        'TC-REC-002: 相似商品推荐',
                        False,
                        '相似商品列表包含原商品本身'
                    )

                return self.log_result(
                    'TC-REC-002: 相似商品推荐',
                    True,
                    f'成功获取{len(items)}个相似商品',
                    {
                        'original_item_id': item_id,
                        'similar_count': len(items),
                        'sample_items': [
                            {'id': i['id'], 'name': i['name']}
                            for i in items[:3]
                        ]
                    }
                )
            else:
                return self.log_result(
                    'TC-REC-002: 相似商品推荐',
                    False,
                    f'请求失败: {response.status_code}',
                    response.json()
                )
        except Exception as e:
            return self.log_result('TC-REC-002: 相似商品推荐', False, f'异常: {str(e)}')

    def test_price_suggestion(self):
        """TC-REC-003: 测试价格建议功能"""
        try:
            # 获取一个类目ID
            response = requests.get(
                f'{self.base_url}/api/categories',
                headers=self.get_headers()
            )

            if response.status_code != 200:
                return self.log_result(
                    'TC-REC-003: 价格建议',
                    False,
                    '无法获取类目列表'
                )

            categories = response.json().get('categories', [])
            if not categories:
                return self.log_result(
                    'TC-REC-003: 价格建议',
                    False,
                    '类目列表为空'
                )

            category_id = categories[0]['id']

            # 测试价格建议
            response = requests.get(
                f'{self.base_url}/api/recommendations/price-suggestion',
                headers=self.get_headers(),
                params={'category_id': category_id}
            )

            if response.status_code == 200:
                data = response.json()

                # 验证必要字段
                required_fields = ['average_price', 'median_price', 'min_price', 'max_price']
                missing_fields = [f for f in required_fields if f not in data]

                if missing_fields:
                    return self.log_result(
                        'TC-REC-003: 价格建议',
                        False,
                        f'价格建议数据不完整，缺少: {missing_fields}',
                        data
                    )

                # 验证价格逻辑合理性
                avg = float(data['average_price'])
                median = float(data['median_price'])
                min_price = float(data['min_price'])
                max_price = float(data['max_price'])

                if not (min_price <= avg <= max_price and min_price <= median <= max_price):
                    return self.log_result(
                        'TC-REC-003: 价格建议',
                        False,
                        '价格数据逻辑不合理',
                        data
                    )

                return self.log_result(
                    'TC-REC-003: 价格建议',
                    True,
                    f'成功获取类目{category_id}的价格建议',
                    {
                        'category_id': category_id,
                        'average_price': avg,
                        'median_price': median,
                        'price_range': f'{min_price}-{max_price}'
                    }
                )
            else:
                return self.log_result(
                    'TC-REC-003: 价格建议',
                    False,
                    f'请求失败: {response.status_code}',
                    response.json()
                )
        except Exception as e:
            return self.log_result('TC-REC-003: 价格建议', False, f'异常: {str(e)}')

    def test_hot_items(self):
        """TC-REC-004: 测试热门商品推荐"""
        try:
            response = requests.get(
                f'{self.base_url}/api/recommendations/hot',
                headers=self.get_headers()
            )

            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])

                if len(items) == 0:
                    return self.log_result(
                        'TC-REC-004: 热门商品推荐',
                        False,
                        '热门商品列表为空'
                    )

                return self.log_result(
                    'TC-REC-004: 热门商品推荐',
                    True,
                    f'成功获取{len(items)}个热门商品',
                    {
                        'count': len(items),
                        'sample_items': [
                            {'id': i['id'], 'name': i['name'], 'views': i.get('view_count', 0)}
                            for i in items[:3]
                        ]
                    }
                )
            else:
                return self.log_result(
                    'TC-REC-004: 热门商品推荐',
                    False,
                    f'请求失败: {response.status_code}',
                    response.json()
                )
        except Exception as e:
            return self.log_result('TC-REC-004: 热门商品推荐', False, f'异常: {str(e)}')

    def test_recommendation_diversity(self):
        """TC-REC-005: 测试推荐多样性"""
        try:
            response = requests.get(
                f'{self.base_url}/api/recommendations/personal',
                headers=self.get_headers()
            )

            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])

                if len(items) < 5:
                    return self.log_result(
                        'TC-REC-005: 推荐多样性',
                        False,
                        f'推荐商品数量不足({len(items)}个)，无法测试多样性'
                    )

                # 统计类目分布
                category_count = {}
                for item in items:
                    cat_id = item.get('category_id')
                    category_count[cat_id] = category_count.get(cat_id, 0) + 1

                # 计算多样性指标
                unique_categories = len(category_count)
                max_same_category = max(category_count.values())
                diversity_score = unique_categories / len(items) * 100

                # 判断多样性是否合理（至少3个不同类目，同类目不超过总数的50%）
                is_diverse = unique_categories >= 3 and max_same_category <= len(items) * 0.5

                return self.log_result(
                    'TC-REC-005: 推荐多样性',
                    is_diverse,
                    f'多样性评分: {diversity_score:.1f}%',
                    {
                        'total_items': len(items),
                        'unique_categories': unique_categories,
                        'max_same_category': max_same_category,
                        'category_distribution': category_count
                    }
                )
            else:
                return self.log_result(
                    'TC-REC-005: 推荐多样性',
                    False,
                    f'请求失败: {response.status_code}'
                )
        except Exception as e:
            return self.log_result('TC-REC-005: 推荐多样性', False, f'异常: {str(e)}')

    def test_recommendation_cache(self):
        """TC-REC-006: 测试推荐缓存机制"""
        try:
            # 第一次请求
            start_time1 = time.time()
            response1 = requests.get(
                f'{self.base_url}/api/recommendations/personal',
                headers=self.get_headers()
            )
            time1 = (time.time() - start_time1) * 1000  # 转换为毫秒

            if response1.status_code != 200:
                return self.log_result(
                    'TC-REC-006: 推荐缓存',
                    False,
                    '第一次请求失败'
                )

            # 第二次请求（应该命中缓存）
            start_time2 = time.time()
            response2 = requests.get(
                f'{self.base_url}/api/recommendations/personal',
                headers=self.get_headers()
            )
            time2 = (time.time() - start_time2) * 1000

            if response2.status_code != 200:
                return self.log_result(
                    'TC-REC-006: 推荐缓存',
                    False,
                    '第二次请求失败'
                )

            # 验证缓存效果（第二次应该更快）
            cache_effective = time2 < time1 * 0.8  # 第二次至少快20%

            return self.log_result(
                'TC-REC-006: 推荐缓存',
                cache_effective,
                f'第一次: {time1:.0f}ms, 第二次: {time2:.0f}ms',
                {
                    'first_request_ms': round(time1, 2),
                    'second_request_ms': round(time2, 2),
                    'speedup': f'{(time1/time2):.2f}x' if time2 > 0 else 'N/A'
                }
            )
        except Exception as e:
            return self.log_result('TC-REC-006: 推荐缓存', False, f'异常: {str(e)}')

    def run_all_tests(self):
        """运行所有推荐功能测试"""
        print("\n" + "="*80)
        print("开始执行 6.2.1 核心推荐功能测试")
        print("="*80 + "\n")

        # 登录
        if not self.login():
            print("\n登录失败，无法继续测试")
            return self.generate_report()

        print()

        # 执行所有测试
        self.test_personal_recommendation()
        self.test_similar_items()
        self.test_price_suggestion()
        self.test_hot_items()
        self.test_recommendation_diversity()
        self.test_recommendation_cache()

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
    tester = RecommendationTester()
    report = tester.run_all_tests()

    # 保存测试报告
    with open('test_report_recommendation.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"测试报告已保存到: test_report_recommendation.json")
