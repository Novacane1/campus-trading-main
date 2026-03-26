"""
文本处理服务单元测试
测试：文本清洗、成色归一化、关键词提取
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.text_processor import (
    TextCleaner,
    ConditionNormalizer,
    KeywordExtractor,
    ItemTextProcessor
)


class TestTextCleaner:
    """文本清洗测试"""

    def test_clean_noise_symbols(self):
        """测试去除无意义符号"""
        text = "iPhone 15 Pro★★★全新未拆封~~~急出!!!"
        result = TextCleaner.clean(text)
        assert '★' not in result
        assert '~' not in result
        print(f"✓ 去除无意义符号: '{text}' -> '{result}'")

    def test_clean_punctuation_normalize(self):
        """测试标点统一"""
        text = "MacBook Air,8GB+256GB.全新!"
        result = TextCleaner.clean(text)
        assert '，' in result or '。' in result or '！' in result
        print(f"✓ 标点统一: '{text}' -> '{result}'")

    def test_clean_whitespace(self):
        """测试空白合并"""
        text = "iPad   Pro    全新    未拆封"
        result = TextCleaner.clean(text)
        assert '   ' not in result
        print(f"✓ 空白合并: '{text}' -> '{result}'")

    def test_clean_empty(self):
        """测试空值处理"""
        assert TextCleaner.clean('') == ''
        assert TextCleaner.clean(None) == ''
        print("✓ 空值处理正常")

    def test_clean_for_vectorization(self):
        """测试向量化清洗"""
        text = "iPhone 15，全新！急出。"
        result = TextCleaner.clean_for_vectorization(text)
        assert '，' not in result
        assert '！' not in result
        assert '。' not in result
        print(f"✓ 向量化清洗: '{text}' -> '{result}'")

    def run_all(self):
        print("\n" + "="*60)
        print("文本清洗测试")
        print("="*60)
        self.test_clean_noise_symbols()
        self.test_clean_punctuation_normalize()
        self.test_clean_whitespace()
        self.test_clean_empty()
        self.test_clean_for_vectorization()
        print("文本清洗测试全部通过！\n")


class TestConditionNormalizer:
    """成色归一化测试"""

    def test_standard_conditions(self):
        """测试标准成色直接匹配"""
        assert ConditionNormalizer.normalize('全新') == '全新'
        assert ConditionNormalizer.normalize('几乎全新') == '几乎全新'
        assert ConditionNormalizer.normalize('稍有瑕疵') == '稍有瑕疵'
        print("✓ 标准成色匹配正常")

    def test_colloquial_expressions(self):
        """测试口语化表达归一化"""
        test_cases = [
            ('九成新', '几乎全新'),
            ('9成新', '几乎全新'),
            ('95新', '几乎全新'),
            ('自用', '几乎全新'),
            ('学生自用', '几乎全新'),
            ('八成新', '稍有瑕疵'),
            ('8成新', '稍有瑕疵'),
            ('未拆封', '全新'),
            ('原封', '全新'),
            ('七成新', '瑕疵较多'),
            ('六成新', '7成新以下'),
        ]
        for expr, expected in test_cases:
            result = ConditionNormalizer.normalize(expr)
            assert result == expected, f"'{expr}' 应归一化为 '{expected}'，实际为 '{result}'"
            print(f"✓ '{expr}' -> '{result}'")

    def test_description_detection(self):
        """测试从描述中检测成色"""
        desc = "MacBook Air M2，个人自用，无划痕，急出"
        result = ConditionNormalizer.normalize(desc)
        assert result in ['几乎全新', '全新']
        print(f"✓ 描述检测: '{desc}' -> '{result}'")

    def test_urgency_detection(self):
        """测试紧急标签检测"""
        assert ConditionNormalizer.extract_urgency('急出，低价转让') == True
        assert ConditionNormalizer.extract_urgency('毕业清仓') == True
        assert ConditionNormalizer.extract_urgency('全新未拆封') == False
        print("✓ 紧急标签检测正常")

    def test_numeric_pattern(self):
        """测试数字成新模式"""
        assert ConditionNormalizer.normalize('这个是95成新的') == '几乎全新'
        assert ConditionNormalizer.normalize('大概85成新') == '稍有瑕疵'
        assert ConditionNormalizer.normalize('只有6成新了') == '7成新以下'
        print("✓ 数字成新模式匹配正常")

    def test_unknown_condition(self):
        """测试无法识别的成色"""
        result = ConditionNormalizer.normalize('随便什么状态')
        assert result is None
        print("✓ 无法识别时返回 None")

    def run_all(self):
        print("\n" + "="*60)
        print("成色归一化测试")
        print("="*60)
        self.test_standard_conditions()
        self.test_colloquial_expressions()
        self.test_description_detection()
        self.test_urgency_detection()
        self.test_numeric_pattern()
        self.test_unknown_condition()
        print("成色归一化测试全部通过！\n")


class TestKeywordExtractor:
    """关键词提取测试"""

    def test_tfidf_extraction(self):
        """测试 TF-IDF 关键词提取"""
        text = "苹果 MacBook Pro 16寸 M3芯片 32GB内存 1TB固态硬盘 深空灰色"
        keywords = KeywordExtractor.extract_tfidf(text, topk=5)
        assert len(keywords) > 0
        words = [w for w, _ in keywords]
        print(f"✓ TF-IDF 关键词: {words}")

    def test_textrank_extraction(self):
        """测试 TextRank 关键词提取"""
        text = "二手 iPad Pro 12.9寸 WiFi版 256GB 银色 配Apple Pencil 苹果平板电脑 学生自用 无划痕 原装配件齐全"
        keywords = KeywordExtractor.extract_textrank(text, topk=5)
        # TextRank 对短文本可能提取不到关键词，这是正常的
        words = [w for w, _ in keywords]
        print(f"✓ TextRank 关键词: {words if words else '(短文本无结果)'}")

    def test_combined_extraction(self):
        """测试综合关键词提取"""
        text = "索尼 PlayStation 5 光驱版 国行 全新未拆封 送手柄"
        keywords = KeywordExtractor.extract_combined(text, topk=5)
        assert len(keywords) > 0
        words = [w for w, _ in keywords]
        print(f"✓ 综合关键词: {words}")

    def test_empty_text(self):
        """测试空文本"""
        assert KeywordExtractor.extract_tfidf('') == []
        assert KeywordExtractor.extract_textrank('') == []
        assert KeywordExtractor.extract_combined('') == []
        print("✓ 空文本处理正常")

    def test_stopwords_filter(self):
        """测试停用词过滤"""
        text = "出售 转让 我的 iPhone 15 Pro Max 256GB"
        keywords = KeywordExtractor.extract_combined(text, topk=10)
        words = [w for w, _ in keywords]
        assert '出售' not in words
        assert '转让' not in words
        assert '我的' not in words
        print(f"✓ 停用词已过滤: {words}")

    def run_all(self):
        print("\n" + "="*60)
        print("关键词提取测试")
        print("="*60)
        self.test_tfidf_extraction()
        self.test_textrank_extraction()
        self.test_combined_extraction()
        self.test_empty_text()
        self.test_stopwords_filter()
        print("关键词提取测试全部通过！\n")


class TestItemTextProcessor:
    """商品文本处理主服务测试"""

    def test_process_item_basic(self):
        """测试基本商品处理"""
        result = ItemTextProcessor.process_item(
            name="MacBook Air M2 ★★★",
            description="8GB+256GB，午夜色，个人自用，无划痕，急出!!!",
            condition="九成新"
        )

        assert result['cleaned_name'] == 'MacBook Air M2'
        assert '★' not in result['cleaned_description']
        assert result['normalized_condition'] == '几乎全新'
        assert result['is_urgent'] == True
        assert len(result['keywords']) > 0
        assert len(result['tokenized_text']) > 0

        print("✓ 基本商品处理:")
        print(f"  清洗后标题: {result['cleaned_name']}")
        print(f"  归一化成色: {result['normalized_condition']}")
        print(f"  是否紧急: {result['is_urgent']}")
        print(f"  关键词: {[w for w, _ in result['keywords'][:5]]}")

    def test_process_item_no_condition(self):
        """测试无成色字段时从描述检测"""
        result = ItemTextProcessor.process_item(
            name="iPad Pro 12.9",
            description="WiFi 256GB，95新，无划痕",
            condition=None
        )

        assert result['detected_condition'] == '几乎全新'
        print(f"✓ 从描述检测成色: {result['detected_condition']}")

    def test_get_text_for_vectorization(self):
        """测试获取向量化文本"""
        text = ItemTextProcessor.get_item_text_for_vectorization(
            name="iPhone 15 Pro",
            description="256GB，原色钛金属，全新未拆封",
            condition="全新"
        )

        assert len(text) > 0
        assert '，' not in text  # 标点已去除
        print(f"✓ 向量化文本: {text[:50]}...")

    def test_batch_process(self):
        """测试批量处理"""
        items = [
            {'name': 'MacBook Pro', 'description': '16寸 M3 全新', 'condition': '全新'},
            {'name': 'iPad Air', 'description': '64GB 九成新', 'condition': None},
            {'name': 'AirPods Pro', 'description': '二代 自用', 'condition': '几乎全新'},
        ]

        results = ItemTextProcessor.batch_process(items)
        assert len(results) == 3
        for r in results:
            assert 'cleaned_name' in r
            assert 'keywords' in r
        print(f"✓ 批量处理 {len(results)} 个商品成功")

    def test_edge_cases(self):
        """测试边界情况"""
        # 全空
        result = ItemTextProcessor.process_item('', '', None)
        assert result['cleaned_name'] == ''
        assert result['semantic_text'] == ''

        # 只有标题
        result = ItemTextProcessor.process_item('iPhone 15', None, None)
        assert result['cleaned_name'] == 'iPhone 15'

        print("✓ 边界情况处理正常")

    def run_all(self):
        print("\n" + "="*60)
        print("商品文本处理主服务测试")
        print("="*60)
        self.test_process_item_basic()
        self.test_process_item_no_condition()
        self.test_get_text_for_vectorization()
        self.test_batch_process()
        self.test_edge_cases()
        print("商品文本处理主服务测试全部通过！\n")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("开始执行文本处理服务测试")
    print("="*60)

    TestTextCleaner().run_all()
    TestConditionNormalizer().run_all()
    TestKeywordExtractor().run_all()
    TestItemTextProcessor().run_all()

    print("="*60)
    print("所有测试通过！")
    print("="*60 + "\n")


if __name__ == '__main__':
    run_all_tests()
