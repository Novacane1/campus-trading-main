"""
6.2.3 前后端交互测试
测试API接口、数据传输、错误处理等功能
"""
import requests
import json
import time
from datetime import datetime

class APIInteractionTester:
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
                    'TC-API-000: 用户登录',
                    True,
                    f'登录成功，用户ID: {self.user_id}'
                )
            else:
                return self.log_result(
                    'TC-API-000: 用户登录',
                    False,
                    f'登录失败: {response.status_code}'
                )
        except Exception as e:
            return self.log_result('TC-API-000: 用户登录', False, f'异常: {str(e)}')

    def get_headers(self):
        """获取请求头"""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def test_cors_headers(self):
        """TC-API-001: 测试CORS跨域配置"""
        try:
            response = requests.options(
                f'{self.base_url}/api/items',
                headers={'Origin': 'http://localhost:3000'}
            )

            # 检查CORS头
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }

            has_cors = any(cors_headers.values())

            return self.log_result(
                'TC-API-001: CORS跨域配置',
                has_cors,
                'CORS配置正常' if has_cors else 'CORS配置缺失',
                cors_headers
            )
        except Exception as e:
            return self.log_result('TC-API-001: CORS跨域配置', False, f'异常: {str(e)}')

    def test_json_response_format(self):
        """TC-API-002: 测试JSON响应格式"""
        try:
            response = requests.get(
                f'{self.base_url}/api/items',
                headers=self.get_headers()
            )

            # 检查Content-Type
            content_type = response.headers.get('Content-Type', '')
            is_json = 'application/json' in content_type

            if not is_json:
                return self.log_result(
                    'TC-API-002: JSON响应格式',
                    False,
                    f'Content-Type不正确: {content_type}'
                )

            # 尝试解析JSON
            try:
                data = response.json()
                return self.log_result(
                    'TC-API-002: JSON响应格式',
                    True,
                    'JSON格式正确',
                    {'content_type': content_type}
                )
            except json.JSONDecodeError:
                return self.log_result(
                    'TC-API-002: JSON响应格式',
                    False,
                    'JSON解析失败'
                )
        except Exception as e:
            return self.log_result('TC-API-002: JSON响应格式', False, f'异常: {str(e)}')

    def test_pagination(self):
        """TC-API-003: 测试分页功能"""
        try:
            # 测试第一页
            response1 = requests.get(
                f'{self.base_url}/api/items',
                headers=self.get_headers(),
                params={'page': 1, 'per_page': 5}
            )

            if response1.status_code != 200:
                return self.log_result(
                    'TC-API-003: 分页功能',
                    False,
                    f'第一页请求失败: {response1.status_code}'
                )

            data1 = response1.json()

            # 验证分页字段
            required_fields = ['items', 'total', 'page', 'per_page', 'pages']
            missing_fields = [f for f in required_fields if f not in data1]

            if missing_fields:
                return self.log_result(
                    'TC-API-003: 分页功能',
                    False,
                    f'分页字段不完整，缺少: {missing_fields}'
                )

            # 测试第二页
            response2 = requests.get(
                f'{self.base_url}/api/items',
                headers=self.get_headers(),
                params={'page': 2, 'per_page': 5}
            )

            if response2.status_code != 200:
                return self.log_result(
                    'TC-API-003: 分页功能',
                    False,
                    f'第二页请求失败: {response2.status_code}'
                )

            data2 = response2.json()

            # 验证两页数据不同
            items1_ids = [i['id'] for i in data1.get('items', [])]
            items2_ids = [i['id'] for i in data2.get('items', [])]
            no_overlap = not set(items1_ids) & set(items2_ids)

            return self.log_result(
                'TC-API-003: 分页功能',
                no_overlap,
                '分页功能正常' if no_overlap else '分页数据重复',
                {
                    'page1_count': len(items1_ids),
                    'page2_count': len(items2_ids),
                    'total': data1.get('total')
                }
            )
        except Exception as e:
            return self.log_result('TC-API-003: 分页功能', False, f'异常: {str(e)}')

    def test_error_handling(self):
        """TC-API-004: 测试错误处理"""
        try:
            # 测试404错误
            response = requests.get(
                f'{self.base_url}/api/items/999999',
                headers=self.get_headers()
            )

            if response.status_code == 404:
                try:
                    error_data = response.json()
                    has_error_message = 'error' in error_data or 'message' in error_data

                    return self.log_result(
                        'TC-API-004: 错误处理',
                        has_error_message,
                        '404错误处理正常' if has_error_message else '错误信息缺失',
                        {'status_code': 404, 'response': error_data}
                    )
                except json.JSONDecodeError:
                    return self.log_result(
                        'TC-API-004: 错误处理',
                        False,
                        '错误响应不是JSON格式'
                    )
            else:
                return self.log_result(
                    'TC-API-004: 错误处理',
                    False,
                    f'期望404，实际: {response.status_code}'
                )
        except Exception as e:
            return self.log_result('TC-API-004: 错误处理', False, f'异常: {str(e)}')

    def test_authentication_required(self):
        """TC-API-005: 测试身份认证要求"""
        try:
            # 不带Token访问受保护接口
            response = requests.get(f'{self.base_url}/api/users/me')

            if response.status_code == 401:
                return self.log_result(
                    'TC-API-005: 身份认证要求',
                    True,
                    '未授权访问被正确拦截',
                    {'status_code': 401}
                )
            else:
                return self.log_result(
                    'TC-API-005: 身份认证要求',
                    False,
                    f'期望401，实际: {response.status_code}'
                )
        except Exception as e:
            return self.log_result('TC-API-005: 身份认证要求', False, f'异常: {str(e)}')

    def test_input_validation(self):
        """TC-API-006: 测试输入验证"""
        try:
            # 测试无效的分页参数
            response = requests.get(
                f'{self.base_url}/api/items',
                headers=self.get_headers(),
                params={'page': -1, 'per_page': 0}
            )

            # 应该返回400或使用默认值
            is_handled = response.status_code in [400, 200]

            if response.status_code == 200:
                data = response.json()
                # 检查是否使用了默认值
                page = data.get('page', 0)
                per_page = data.get('per_page', 0)
                uses_defaults = page > 0 and per_page > 0

                return self.log_result(
                    'TC-API-006: 输入验证',
                    uses_defaults,
                    '输入验证正常（使用默认值）' if uses_defaults else '输入验证异常',
                    {'page': page, 'per_page': per_page}
                )
            else:
                return self.log_result(
                    'TC-API-006: 输入验证',
                    is_handled,
                    f'输入验证正常（返回{response.status_code}）'
                )
        except Exception as e:
            return self.log_result('TC-API-006: 输入验证', False, f'异常: {str(e)}')

    def test_response_time(self):
        """TC-API-007: 测试响应时间"""
        try:
            endpoints = [
                ('/api/items', 'GET', None),
                ('/api/recommendations/personal', 'GET', None),
                ('/api/categories', 'GET', None)
            ]

            results = []
            all_fast = True

            for endpoint, method, data in endpoints:
                start_time = time.time()

                if method == 'GET':
                    response = requests.get(
                        f'{self.base_url}{endpoint}',
                        headers=self.get_headers()
                    )
                else:
                    response = requests.post(
                        f'{self.base_url}{endpoint}',
                        headers=self.get_headers(),
                        json=data
                    )

                elapsed = (time.time() - start_time) * 1000  # 转换为毫秒

                is_fast = elapsed < 500  # 500ms阈值
                all_fast = all_fast and is_fast

                results.append({
                    'endpoint': endpoint,
                    'response_time_ms': round(elapsed, 2),
                    'is_fast': is_fast
                })

            return self.log_result(
                'TC-API-007: 响应时间',
                all_fast,
                '所有接口响应时间正常' if all_fast else '部分接口响应较慢',
                {'endpoints': results}
            )
        except Exception as e:
            return self.log_result('TC-API-007: 响应时间', False, f'异常: {str(e)}')

    def test_data_consistency(self):
        """TC-API-008: 测试数据一致性"""
        try:
            # 获取商品列表
            response1 = requests.get(
                f'{self.base_url}/api/items',
                headers=self.get_headers(),
                params={'page': 1, 'per_page': 1}
            )

            if response1.status_code != 200:
                return self.log_result(
                    'TC-API-008: 数据一致性',
                    False,
                    '无法获取商品列表'
                )

            items = response1.json().get('items', [])
            if not items:
                return self.log_result(
                    'TC-API-008: 数据一致性',
                    False,
                    '商品列表为空'
                )

            item_id = items[0]['id']

            # 获取商品详情
            response2 = requests.get(
                f'{self.base_url}/api/items/{item_id}',
                headers=self.get_headers()
            )

            if response2.status_code != 200:
                return self.log_result(
                    'TC-API-008: 数据一致性',
                    False,
                    '无法获取商品详情'
                )

            item_detail = response2.json()

            # 比较关键字段是否一致
            list_item = items[0]
            key_fields = ['id', 'name', 'price']
            inconsistent_fields = []

            for field in key_fields:
                if str(list_item.get(field)) != str(item_detail.get(field)):
                    inconsistent_fields.append(field)

            is_consistent = len(inconsistent_fields) == 0

            return self.log_result(
                'TC-API-008: 数据一致性',
                is_consistent,
                '数据一致' if is_consistent else f'数据不一致: {inconsistent_fields}',
                {
                    'item_id': item_id,
                    'inconsistent_fields': inconsistent_fields
                }
            )
        except Exception as e:
            return self.log_result('TC-API-008: 数据一致性', False, f'异常: {str(e)}')

    def run_all_tests(self):
        """运行所有API交互测试"""
        print("\n" + "="*80)
        print("开始执行 6.2.3 前后端交互测试")
        print("="*80 + "\n")

        # 登录
        if not self.login():
            print("\n登录失败，无法继续测试")
            return self.generate_report()

        print()

        # 执行所有测试
        self.test_cors_headers()
        self.test_json_response_format()
        self.test_pagination()
        self.test_error_handling()
        self.test_authentication_required()
        self.test_input_validation()
        self.test_response_time()
        self.test_data_consistency()

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
    tester = APIInteractionTester()
    report = tester.run_all_tests()

    # 保存测试报告
    with open('test_report_api_interaction.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"测试报告已保存到: test_report_api_interaction.json")
