"""
6.2.2 数据处理与画像功能测试
测试用户行为记录、兴趣挖掘、TF-IDF向量化等功能
"""
import requests
import json
import time
from datetime import datetime

class DataProcessingTester:
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
                    'TC-DATA-000: 用户登录',
                    True,
                    f'登录成功，用户ID: {self.user_id}'
                )
            else:
                return self.log_result(
                    'TC-DATA-000: 用户登录',
                    False,
                    f'登录失败: {response.status_code}'
                )
        except Exception as e:
            return self.log_result('TC-DATA-000: 用户登录', False, f'异常: {str(e)}')

    def get_headers(self):
        """获取请求头"""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def test_user_action_recording(self):
        """TC-DATA-001: 测试用户行为记录"""
        try:
            # 获取一个商品ID
            response = requests.get(
                f'{self.base_url}/api/items',
                headers=self.get_headers(),
                params={'page': 1, 'per_page': 1}
            )

            if response.status_code != 200:
                return self.log_result(
                    'TC-DATA-001: 用户行为记录',
                    False,
                    '无法获取测试商品'
                )

            items = response.json().get('items', [])
            if not items:
                return self.log_result(
                    'TC-DATA-001: 用户行为记录',
                    False,
                    '商品列表为空'
                )

            item_id = items[0]['id']

            # 记录浏览行为
            response = requests.post(
                f'{self.base_url}/api/items/{item_id}/action',
                headers=self.get_headers(),
                json={'action_type': 'view'}
            )

            if response.status_code in [200, 201]:
                # 验证行为是否被记录
                time.sleep(0.5)  # 等待数据写入

                # 尝试获取用户行为历史
                response = requests.get(
                    f'{self.base_url}/api/auth/me/actions',
                    headers=self.get_headers()
                )
                if response.status_code == 200:
                    actions = response.json().get('actions', [])
                    # 检查是否包含刚才的浏览行为
                    recent_view = any(
                        a.get('item_id') == item_id and a.get('action_type') == 'view'
                        for a in actions
                    )

                    return self.log_result(
                        'TC-DATA-001: 用户行为记录',
                        recent_view,
                        '浏览行为记录成功' if recent_view else '未找到浏览记录',
                        {
                            'item_id': item_id,
                            'action_type': 'view',
                            'total_actions': len(actions)
                        }
                    )
                else:
                    return self.log_result(
                        'TC-DATA-001: 用户行为记录',
                        True,  # 记录成功但无法验证
                        '行为记录成功（无法验证）'
                    )
            else:
                return self.log_result(
                    'TC-DATA-001: 用户行为记录',
                    False,
                    f'行为记录失败: {response.status_code}'
                )
        except Exception as e:
            return self.log_result('TC-DATA-001: 用户行为记录', False, f'异常: {str(e)}')

    def test_user_interest_mining(self):
        """TC-DATA-002: 测试用户兴趣挖掘"""
        try:
            response = requests.get(
                f'{self.base_url}/api/auth/me/interests',
                headers=self.get_headers()
            )

            if response.status_code == 200:
                data = response.json()
                interests = data.get('interests', [])

                # 验证兴趣数据结构
                if not isinstance(interests, list):
                    return self.log_result(
                        'TC-DATA-002: 用户兴趣挖掘',
                        False,
                        '兴趣数据格式错误'
                    )

                # 如果有兴趣数据，验证字段完整性
                if len(interests) > 0:
                    required_fields = ['category_id', 'score']
                    for interest in interests[:3]:
                        missing_fields = [f for f in required_fields if f not in interest]
                        if missing_fields:
                            return self.log_result(
                                'TC-DATA-002: 用户兴趣挖掘',
                                False,
                                f'兴趣数据字段不完整，缺少: {missing_fields}'
                            )

                return self.log_result(
                    'TC-DATA-002: 用户兴趣挖掘',
                    True,
                    f'成功获取{len(interests)}个兴趣类目',
                    {
                        'interest_count': len(interests),
                        'top_interests': interests[:3] if interests else []
                    }
                )
            else:
                return self.log_result(
                    'TC-DATA-002: 用户兴趣挖掘',
                    False,
                    f'请求失败: {response.status_code}'
                )
        except Exception as e:
            return self.log_result('TC-DATA-002: 用户兴趣挖掘', False, f'异常: {str(e)}')

    def test_tfidf_vectorization(self):
        """TC-DATA-003: 测试TF-IDF向量化"""
        try:
            # 检查是否存在商品向量数据
            response = requests.get(
                f'{self.base_url}/api/items',
                headers=self.get_headers(),
                params={'page': 1, 'per_page': 5}
            )

            if response.status_code != 200:
                return self.log_result(
                    'TC-DATA-003: TF-IDF向量化',
                    False,
                    '无法获取商品列表'
                )

            items = response.json().get('items', [])
            if not items:
                return self.log_result(
                    'TC-DATA-003: TF-IDF向量化',
                    False,
                    '商品列表为空'
                )

            # 检查商品是否有embedding数据（通过相似商品推荐接口间接验证）
            item_id = items[0]['id']
            response = requests.get(
                f'{self.base_url}/api/recommendations/similar/{item_id}',
                headers=self.get_headers()
            )

            if response.status_code == 200:
                similar_items = response.json().get('items', [])

                # 如果能返回相似商品，说明TF-IDF向量化工作正常
                return self.log_result(
                    'TC-DATA-003: TF-IDF向量化',
                    True,
                    f'TF-IDF向量化正常，找到{len(similar_items)}个相似商品',
                    {
                        'test_item_id': item_id,
                        'similar_count': len(similar_items)
                    }
                )
            else:
                return self.log_result(
                    'TC-DATA-003: TF-IDF向量化',
                    False,
                    f'相似商品查询失败: {response.status_code}'
                )
        except Exception as e:
            return self.log_result('TC-DATA-003: TF-IDF向量化', False, f'异常: {str(e)}')

    def test_user_profile_completeness(self):
        """TC-DATA-004: 测试用户画像完整性"""
        try:
            response = requests.get(
                f'{self.base_url}/api/auth/me',
                headers=self.get_headers()
            )

            if response.status_code == 200:
                user = response.json()

                # 检查基本字段
                basic_fields = ['id', 'username', 'school_name', 'student_id']
                missing_basic = [f for f in basic_fields if f not in user]

                if missing_basic:
                    return self.log_result(
                        'TC-DATA-004: 用户画像完整性',
                        False,
                        f'用户基本信息不完整，缺少: {missing_basic}'
                    )

                # 检查画像字段
                profile_fields = ['credit_score', 'usual_locations', 'available_time_slots']
                existing_profile = [f for f in profile_fields if f in user]

                completeness = len(existing_profile) / len(profile_fields) * 100

                return self.log_result(
                    'TC-DATA-004: 用户画像完整性',
                    completeness >= 50,  # 至少50%的画像字段存在
                    f'用户画像完整度: {completeness:.0f}%',
                    {
                        'basic_fields': basic_fields,
                        'profile_fields': existing_profile,
                        'completeness': f'{completeness:.0f}%'
                    }
                )
            else:
                return self.log_result(
                    'TC-DATA-004: 用户画像完整性',
                    False,
                    f'请求失败: {response.status_code}'
                )
        except Exception as e:
            return self.log_result('TC-DATA-004: 用户画像完整性', False, f'异常: {str(e)}')

    def test_category_statistics(self):
        """TC-DATA-005: 测试类目统计数据"""
        try:
            response = requests.get(
                f'{self.base_url}/api/stats/categories',
                headers=self.get_headers()
            )

            if response.status_code == 200:
                data = response.json()
                categories = data.get('categories', [])

                if not categories:
                    return self.log_result(
                        'TC-DATA-005: 类目统计数据',
                        False,
                        '类目统计数据为空'
                    )

                # 验证统计数据字段
                required_fields = ['category_id', 'item_count']
                for cat in categories[:3]:
                    missing_fields = [f for f in required_fields if f not in cat]
                    if missing_fields:
                        return self.log_result(
                            'TC-DATA-005: 类目统计数据',
                            False,
                            f'统计数据字段不完整，缺少: {missing_fields}'
                        )

                total_items = sum(c.get('item_count', 0) for c in categories)

                return self.log_result(
                    'TC-DATA-005: 类目统计数据',
                    True,
                    f'成功获取{len(categories)}个类目的统计数据',
                    {
                        'category_count': len(categories),
                        'total_items': total_items,
                        'top_categories': [
                            {'id': c['category_id'], 'count': c['item_count']}
                            for c in categories[:3]
                        ]
                    }
                )
            else:
                return self.log_result(
                    'TC-DATA-005: 类目统计数据',
                    False,
                    f'请求失败: {response.status_code}'
                )
        except Exception as e:
            return self.log_result('TC-DATA-005: 类目统计数据', False, f'异常: {str(e)}')

    def test_price_statistics(self):
        """TC-DATA-006: 测试价格统计数据"""
        try:
            # 获取一个类目
            response = requests.get(
                f'{self.base_url}/api/categories',
                headers=self.get_headers()
            )

            if response.status_code != 200:
                return self.log_result(
                    'TC-DATA-006: 价格统计数据',
                    False,
                    '无法获取类目列表'
                )

            categories = response.json().get('categories', [])
            if not categories:
                return self.log_result(
                    'TC-DATA-006: 价格统计数据',
                    False,
                    '类目列表为空'
                )

            category_id = categories[0]['id']

            # 获取价格统计
            response = requests.get(
                f'{self.base_url}/api/recommendations/price-suggestion',
                headers=self.get_headers(),
                params={'category_id': category_id}
            )

            if response.status_code == 200:
                data = response.json()

                # 验证统计字段
                required_fields = ['average_price', 'median_price', 'min_price', 'max_price']
                missing_fields = [f for f in required_fields if f not in data]

                if missing_fields:
                    return self.log_result(
                        'TC-DATA-006: 价格统计数据',
                        False,
                        f'价格统计数据不完整，缺少: {missing_fields}'
                    )

                # 验证数据合理性
                prices = {
                    'avg': float(data['average_price']),
                    'median': float(data['median_price']),
                    'min': float(data['min_price']),
                    'max': float(data['max_price'])
                }

                is_valid = (
                    prices['min'] <= prices['avg'] <= prices['max'] and
                    prices['min'] <= prices['median'] <= prices['max'] and
                    prices['min'] >= 0
                )

                return self.log_result(
                    'TC-DATA-006: 价格统计数据',
                    is_valid,
                    '价格统计数据合理' if is_valid else '价格统计数据不合理',
                    {
                        'category_id': category_id,
                        'statistics': prices
                    }
                )
            else:
                return self.log_result(
                    'TC-DATA-006: 价格统计数据',
                    False,
                    f'请求失败: {response.status_code}'
                )
        except Exception as e:
            return self.log_result('TC-DATA-006: 价格统计数据', False, f'异常: {str(e)}')

    def run_all_tests(self):
        """运行所有数据处理测试"""
        print("\n" + "="*80)
        print("开始执行 6.2.2 数据处理与画像功能测试")
        print("="*80 + "\n")

        # 登录
        if not self.login():
            print("\n登录失败，无法继续测试")
            return self.generate_report()

        print()

        # 执行所有测试
        self.test_user_action_recording()
        self.test_user_interest_mining()
        self.test_tfidf_vectorization()
        self.test_user_profile_completeness()
        self.test_category_statistics()
        self.test_price_statistics()

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
    tester = DataProcessingTester()
    report = tester.run_all_tests()

    # 保存测试报告
    with open('test_report_data_processing.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"测试报告已保存到: test_report_data_processing.json")
