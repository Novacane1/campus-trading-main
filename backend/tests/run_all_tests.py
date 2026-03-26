#!/usr/bin/env python3
"""
完整系统测试套件
按照论文第六章测试大纲执行所有测试
"""
import sys
import os
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_recommendation import RecommendationTester
from test_data_processing import DataProcessingTester
from test_api_interaction import APIInteractionTester
from test_performance import PerformanceTester
from test_security import SecurityTester


class TestRunner:
    def __init__(self):
        self.base_url = 'http://localhost:5001'
        self.all_results = []
        self.start_time = None
        self.end_time = None

    def print_header(self, title):
        """打印测试章节标题"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")

    def print_section(self, title):
        """打印测试小节标题"""
        print("\n" + "-" * 80)
        print(f"  {title}")
        print("-" * 80 + "\n")

    def run_test_section(self, tester_class, section_name, test_methods):
        """运行一个测试章节"""
        self.print_section(section_name)
        tester = tester_class(self.base_url)

        # 登录
        if hasattr(tester, 'login'):
            tester.login()

        # 运行测试方法
        for method_name in test_methods:
            if hasattr(tester, method_name):
                method = getattr(tester, method_name)
                try:
                    method()
                except Exception as e:
                    print(f"✗ FAIL | {method_name}: 异常 - {str(e)}")

        # 收集结果
        if hasattr(tester, 'test_results'):
            self.all_results.extend(tester.test_results)

        return tester

    def generate_report(self):
        """生成测试报告"""
        self.print_header("6.4 测试结果分析")

        # 统计结果
        total_tests = len(self.all_results)
        passed_tests = sum(1 for r in self.all_results if r['passed'])
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # 按模块分类统计
        module_stats = {}
        for result in self.all_results:
            test_name = result['test_name']
            module = test_name.split(':')[0].split('-')[1] if '-' in test_name else 'OTHER'

            if module not in module_stats:
                module_stats[module] = {'total': 0, 'passed': 0, 'failed': 0}

            module_stats[module]['total'] += 1
            if result['passed']:
                module_stats[module]['passed'] += 1
            else:
                module_stats[module]['failed'] += 1

        # 打印总体统计
        print("\n6.4.1 功能完整性评估")
        print("-" * 80)
        print(f"测试总数: {total_tests}")
        print(f"通过数量: {passed_tests}")
        print(f"失败数量: {failed_tests}")
        print(f"通过率: {pass_rate:.2f}%")
        print(f"测试时长: {(self.end_time - self.start_time).total_seconds():.2f}秒")

        # 打印模块统计
        print("\n按模块统计:")
        print(f"{'模块':<15} {'总数':<8} {'通过':<8} {'失败':<8} {'通过率':<10}")
        print("-" * 60)

        module_names = {
            'REC': '推荐系统',
            'DATA': '数据处理',
            'API': '接口交互',
            'PERF': '性能测试',
            'SEC': '安全测试'
        }

        for module, stats in sorted(module_stats.items()):
            module_name = module_names.get(module, module)
            pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"{module_name:<15} {stats['total']:<8} {stats['passed']:<8} {stats['failed']:<8} {pass_rate:.2f}%")

        # 打印失败的测试
        failed_results = [r for r in self.all_results if not r['passed']]
        if failed_results:
            print("\n失败的测试用例:")
            print("-" * 80)
            for result in failed_results:
                print(f"✗ {result['test_name']}")
                print(f"  原因: {result['message']}")
                if result.get('details'):
                    print(f"  详情: {json.dumps(result['details'], ensure_ascii=False)}")

        # 保存详细报告
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'pass_rate': pass_rate,
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'duration_seconds': (self.end_time - self.start_time).total_seconds()
            },
            'module_stats': module_stats,
            'all_results': self.all_results
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        print(f"\n详细测试报告已保存至: {report_file}")

        # 6.4.2 系统稳定性与精准度评估
        print("\n6.4.2 系统稳定性与精准度评估")
        print("-" * 80)

        # 分析推荐系统测试结果
        rec_results = [r for r in self.all_results if 'REC' in r['test_name']]
        if rec_results:
            rec_passed = sum(1 for r in rec_results if r['passed'])
            rec_total = len(rec_results)
            print(f"推荐系统稳定性: {rec_passed}/{rec_total} ({rec_passed/rec_total*100:.2f}%)")

        # 分析性能测试结果
        perf_results = [r for r in self.all_results if 'PERF' in r['test_name']]
        if perf_results:
            perf_passed = sum(1 for r in perf_results if r['passed'])
            perf_total = len(perf_results)
            print(f"性能测试通过率: {perf_passed}/{perf_total} ({perf_passed/perf_total*100:.2f}%)")

        # 分析安全测试结果
        sec_results = [r for r in self.all_results if 'SEC' in r['test_name']]
        if sec_results:
            sec_passed = sum(1 for r in sec_results if r['passed'])
            sec_total = len(sec_results)
            print(f"安全测试通过率: {sec_passed}/{sec_total} ({sec_passed/sec_total*100:.2f}%)")

        print("\n" + "=" * 80)
        print("测试完成！")
        print("=" * 80)

        return pass_rate >= 90  # 90%通过率视为成功

    def run_all_tests(self):
        """运行所有测试"""
        self.start_time = datetime.now()

        print("\n" + "=" * 80)
        print("  校园二手交易平台 - 完整系统测试")
        print("  按照论文第六章测试大纲执行")
        print("=" * 80)
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试环境: {self.base_url}")

        # 6.1 测试环境与方法
        self.print_header("6.1 测试环境与方法")
        print("6.1.1 测试环境搭建")
        print("  ✓ 后端服务: Flask 3.0.0")
        print("  ✓ 数据库: PostgreSQL 14.x")
        print("  ✓ 缓存: Redis 7.x")
        print("  ✓ Python: 3.10+")
        print("\n6.1.2 测试方法与工具")
        print("  ✓ 功能测试: requests库")
        print("  ✓ 性能测试: 并发请求模拟")
        print("  ✓ 安全测试: 漏洞扫描")

        # 6.2 功能测试
        self.print_header("6.2 功能测试")

        # 6.2.1 核心推荐功能测试
        self.run_test_section(
            RecommendationTester,
            "6.2.1 核心推荐功能测试",
            [
                'test_personal_recommendation',
                'test_similar_items',
                'test_hot_items',
                'test_category_recommendation',
                'test_price_suggestion',
                'test_recommendation_diversity',
                'test_recommendation_freshness',
                'test_collaborative_filtering'
            ]
        )

        # 6.2.2 数据处理与画像功能测试
        self.run_test_section(
            DataProcessingTester,
            "6.2.2 数据处理与画像功能测试",
            [
                'test_user_action_recording',
                'test_user_interest_extraction',
                'test_tfidf_vectorization',
                'test_item_clustering',
                'test_price_statistics',
                'test_user_profile_building',
                'test_behavior_analysis'
            ]
        )

        # 6.2.3 前后端交互测试
        self.run_test_section(
            APIInteractionTester,
            "6.2.3 前后端交互测试",
            [
                'test_cors_headers',
                'test_json_response_format',
                'test_pagination',
                'test_error_handling',
                'test_jwt_authentication',
                'test_token_expiration',
                'test_request_validation',
                'test_file_upload'
            ]
        )

        # 6.3 性能与安全测试
        self.print_header("6.3 性能与安全测试")

        # 6.3.1 响应时间与并发处理测试
        self.run_test_section(
            PerformanceTester,
            "6.3.1 响应时间与并发处理测试",
            [
                'test_login_performance',
                'test_item_list_performance',
                'test_recommendation_performance',
                'test_search_performance',
                'test_concurrent_requests',
                'test_database_query_performance',
                'test_cache_effectiveness'
            ]
        )

        # 6.3.2 隐私保护与权限管控测试
        self.run_test_section(
            SecurityTester,
            "6.3.2 隐私保护与权限管控测试",
            [
                'test_password_encryption',
                'test_jwt_security',
                'test_sql_injection',
                'test_xss_protection',
                'test_sensitive_word_filter',
                'test_unauthorized_access',
                'test_permission_control',
                'test_rate_limiting'
            ]
        )

        self.end_time = datetime.now()

        # 生成测试报告
        success = self.generate_report()

        return 0 if success else 1


if __name__ == '__main__':
    runner = TestRunner()
    exit_code = runner.run_all_tests()
    sys.exit(exit_code)
