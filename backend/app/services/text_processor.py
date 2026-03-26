"""
商品文本数据处理服务
功能：
1. 文本基础清洗（去除无意义符号、统一标点、过滤空白）
2. 成色表达规则归一化（口语化表达标准化）
3. 关键词提取（TF-IDF + TextRank）
"""
import re
import math
from collections import Counter, defaultdict
from typing import List, Dict, Optional, Tuple

import jieba
import jieba.analyse

# ==================== 1. 文本清洗 ====================

class TextCleaner:
    """文本清洗器"""

    # 无意义符号正则（保留中英文、数字、常用标点）
    NOISE_PATTERN = re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9\s，。！？、；：""''（）【】\-\.\,\!\?\;\:\(\)\[\]]')

    # 多空白合并
    MULTI_SPACE_PATTERN = re.compile(r'\s+')

    # 英文标点到中文标点映射
    PUNCT_MAP = {
        ',': '，',
        '.': '。',
        '!': '！',
        '?': '？',
        ';': '；',
        ':': '：',
        '(': '（',
        ')': '）',
        '[': '【',
        ']': '】',
        '"': '"',
        "'": "'",
    }

    # 常见无意义词/表情
    STOPWORDS = {
        '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
        '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
        '自己', '这', '那', '啊', '呢', '吧', '哦', '嗯', '哈', '呀', '哎', '唉',
        '嘻嘻', '哈哈', '呵呵', '嘿嘿', '么么哒', '比心', '加油', '谢谢',
    }

    @classmethod
    def clean(cls, text: str) -> str:
        """
        文本清洗主函数
        1. 去除无意义符号
        2. 统一中英文标点
        3. 合并多余空白
        4. 去除首尾空白
        """
        if not text:
            return ''

        # 去除无意义符号
        text = cls.NOISE_PATTERN.sub(' ', text)

        # 统一标点（英文转中文）
        for en, zh in cls.PUNCT_MAP.items():
            text = text.replace(en, zh)

        # 合并多余空白
        text = cls.MULTI_SPACE_PATTERN.sub(' ', text)

        # 去除首尾空白
        text = text.strip()

        return text

    @classmethod
    def clean_for_vectorization(cls, text: str) -> str:
        """
        用于向量化的深度清洗
        额外去除标点符号，只保留中英文和数字
        """
        text = cls.clean(text)
        # 去除所有标点
        text = re.sub(r'[，。！？、；：""''（）【】\-\.\,\!\?\;\:\(\)\[\]]', ' ', text)
        text = cls.MULTI_SPACE_PATTERN.sub(' ', text)
        return text.strip()

    @classmethod
    def remove_stopwords(cls, words: List[str]) -> List[str]:
        """去除停用词"""
        return [w for w in words if w not in cls.STOPWORDS and len(w.strip()) > 0]


# ==================== 2. 成色归一化 ====================

class ConditionNormalizer:
    """成色表达归一化器"""

    # 标准成色等级
    STANDARD_CONDITIONS = ['全新', '几乎全新', '稍有瑕疵', '瑕疵较多', '7成新以下']

    # 口语化表达到标准成色的映射规则
    CONDITION_RULES = {
        # 全新
        '全新': '全新',
        '崭新': '全新',
        '未拆封': '全新',
        '未开封': '全新',
        '全新未拆': '全新',
        '未使用': '全新',
        '没用过': '全新',
        '没使用': '全新',
        '原封': '全新',
        '在保': '全新',
        '在保修': '全新',

        # 几乎全新
        '几乎全新': '几乎全新',
        '近全新': '几乎全新',
        '准新': '几乎全新',
        '九成新': '几乎全新',
        '9成新': '几乎全新',
        '95新': '几乎全新',
        '99新': '几乎全新',
        '98新': '几乎全新',
        '97新': '几乎全新',
        '96新': '几乎全新',
        '九五新': '几乎全新',
        '九九新': '几乎全新',
        '自用': '几乎全新',
        '个人自用': '几乎全新',
        '学生自用': '几乎全新',
        '轻微使用': '几乎全新',
        '轻度使用': '几乎全新',
        '基本全新': '几乎全新',
        '成色很好': '几乎全新',
        '成色很新': '几乎全新',
        '无明显划痕': '几乎全新',
        '无划痕': '几乎全新',
        '无磨损': '几乎全新',

        # 稍有瑕疵
        '稍有瑕疵': '稍有瑕疵',
        '八成新': '稍有瑕疵',
        '8成新': '稍有瑕疵',
        '85新': '稍有瑕疵',
        '八五新': '稍有瑕疵',
        '有使用痕迹': '稍有瑕疵',
        '正常使用痕迹': '稍有瑕疵',
        '轻微划痕': '稍有瑕疵',
        '小瑕疵': '稍有瑕疵',
        '微瑕': '稍有瑕疵',
        '成色一般': '稍有瑕疵',
        '中等成色': '稍有瑕疵',

        # 瑕疵较多
        '瑕疵较多': '瑕疵较多',
        '七成新': '瑕疵较多',
        '7成新': '瑕疵较多',
        '75新': '瑕疵较多',
        '明显划痕': '瑕疵较多',
        '有磨损': '瑕疵较多',
        '磨损明显': '瑕疵较多',
        '成色较差': '瑕疵较多',

        # 7成新以下
        '7成新以下': '7成新以下',
        '六成新': '7成新以下',
        '6成新': '7成新以下',
        '五成新': '7成新以下',
        '5成新': '7成新以下',
        '老旧': '7成新以下',
        '破旧': '7成新以下',
        '严重磨损': '7成新以下',
    }

    # 紧急程度标签（不影响成色，但可作为附加信息）
    URGENCY_KEYWORDS = ['急出', '急售', '急转', '低价出', '亏本出', '清仓', '毕业清', '搬家出']

    @classmethod
    def normalize(cls, text: str) -> Optional[str]:
        """
        将口语化成色表达归一化为标准成色
        返回标准成色或 None（无法识别时）
        """
        if not text:
            return None

        text = text.strip()

        # 直接匹配
        if text in cls.CONDITION_RULES:
            return cls.CONDITION_RULES[text]

        # 先用正则匹配数字成新（优先级最高，避免子串误匹配）
        # 支持 "95成新"、"9成新"、"95新" 等格式
        match = re.search(r'(\d{1,2})\s*成?\s*新', text)
        if match:
            num = int(match.group(1))
            if num >= 90:
                return '几乎全新'
            elif num >= 80:
                return '稍有瑕疵'
            elif num >= 70:
                return '瑕疵较多'
            else:
                return '7成新以下'

        # 模糊匹配（按关键词长度降序，避免短关键词误匹配）
        sorted_rules = sorted(cls.CONDITION_RULES.items(), key=lambda x: len(x[0]), reverse=True)
        for keyword, standard in sorted_rules:
            if keyword in text:
                return standard

        return None

    @classmethod
    def extract_urgency(cls, text: str) -> bool:
        """检测是否包含紧急出售标签"""
        if not text:
            return False
        for keyword in cls.URGENCY_KEYWORDS:
            if keyword in text:
                return True
        return False

    @classmethod
    def normalize_description(cls, description: str) -> Tuple[str, Optional[str], bool]:
        """
        处理商品描述，提取并归一化成色信息
        返回：(清洗后描述, 识别的成色, 是否紧急)
        """
        if not description:
            return '', None, False

        cleaned = TextCleaner.clean(description)
        condition = cls.normalize(cleaned)
        is_urgent = cls.extract_urgency(cleaned)

        return cleaned, condition, is_urgent


# ==================== 3. 关键词提取 ====================

class KeywordExtractor:
    """关键词提取器"""

    # 商品领域停用词扩展
    DOMAIN_STOPWORDS = {
        '出售', '转让', '出', '卖', '售', '价格', '价', '元', '块',
        '联系', '私聊', '详聊', '可议', '可小刀', '小刀', '刀',
        '同城', '自提', '包邮', '邮费', '运费',
        '需要', '想要', '求购', '收', '要',
    }

    @classmethod
    def extract_tfidf(cls, text: str, topk: int = 10) -> List[Tuple[str, float]]:
        """
        TF-IDF 关键词提取
        返回：[(关键词, 权重), ...]
        """
        if not text:
            return []

        cleaned = TextCleaner.clean_for_vectorization(text)
        keywords = jieba.analyse.extract_tags(
            cleaned,
            topK=topk,
            withWeight=True,
            allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'vn', 'an')  # 名词、动名词、形容词性名词
        )

        # 过滤领域停用词
        filtered = [
            (word, weight) for word, weight in keywords
            if word not in cls.DOMAIN_STOPWORDS and word not in TextCleaner.STOPWORDS
        ]

        return filtered

    @classmethod
    def extract_textrank(cls, text: str, topk: int = 10) -> List[Tuple[str, float]]:
        """
        TextRank 关键词提取
        返回：[(关键词, 权重), ...]
        """
        if not text:
            return []

        cleaned = TextCleaner.clean_for_vectorization(text)
        keywords = jieba.analyse.textrank(
            cleaned,
            topK=topk,
            withWeight=True,
            allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'vn', 'an')
        )

        # 过滤领域停用词
        filtered = [
            (word, weight) for word, weight in keywords
            if word not in cls.DOMAIN_STOPWORDS and word not in TextCleaner.STOPWORDS
        ]

        return filtered

    @classmethod
    def extract_combined(cls, text: str, topk: int = 10) -> List[Tuple[str, float]]:
        """
        综合关键词提取（TF-IDF + TextRank 融合）
        返回：[(关键词, 权重), ...]
        """
        tfidf_kw = dict(cls.extract_tfidf(text, topk * 2))
        textrank_kw = dict(cls.extract_textrank(text, topk * 2))

        # 融合权重（各占50%）
        all_words = set(tfidf_kw.keys()) | set(textrank_kw.keys())
        combined = {}
        for word in all_words:
            score = 0.5 * tfidf_kw.get(word, 0) + 0.5 * textrank_kw.get(word, 0)
            combined[word] = score

        # 排序取 topk
        sorted_kw = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        return sorted_kw[:topk]


# ==================== 4. 商品文本处理主服务 ====================

class ItemTextProcessor:
    """商品文本处理主服务"""

    @classmethod
    def process_item(cls, name: str, description: str, condition: str = None) -> Dict:
        """
        处理单个商品的文本数据
        返回处理结果字典
        """
        # 1. 清洗标题和描述
        cleaned_name = TextCleaner.clean(name) if name else ''
        cleaned_desc = TextCleaner.clean(description) if description else ''

        # 2. 成色归一化
        normalized_condition = condition
        detected_condition = None
        is_urgent = False

        if condition:
            normalized_condition = ConditionNormalizer.normalize(condition) or condition

        # 从描述中检测成色（如果未提供或需要验证）
        if cleaned_desc:
            detected_condition = ConditionNormalizer.normalize(cleaned_desc)
            is_urgent = ConditionNormalizer.extract_urgency(cleaned_desc)

        # 3. 构建统一语义文本
        parts = [cleaned_name]
        if cleaned_desc:
            parts.append(cleaned_desc)
        if normalized_condition:
            parts.append(normalized_condition)
        semantic_text = ' '.join(parts)

        # 4. 分词（用于向量化）
        tokenized = ' '.join(jieba.cut(TextCleaner.clean_for_vectorization(semantic_text)))

        # 5. 关键词提取
        keywords = KeywordExtractor.extract_combined(semantic_text, topk=10)

        return {
            'cleaned_name': cleaned_name,
            'cleaned_description': cleaned_desc,
            'normalized_condition': normalized_condition,
            'detected_condition': detected_condition,
            'is_urgent': is_urgent,
            'semantic_text': semantic_text,
            'tokenized_text': tokenized,
            'keywords': keywords,
        }

    @classmethod
    def get_item_text_for_vectorization(cls, name: str, description: str, condition: str = None) -> str:
        """
        获取用于 TF-IDF 向量化的处理后文本
        """
        result = cls.process_item(name, description, condition)
        return result['tokenized_text']

    @classmethod
    def batch_process(cls, items: List[Dict]) -> List[Dict]:
        """
        批量处理商品文本
        items: [{'name': ..., 'description': ..., 'condition': ...}, ...]
        """
        results = []
        for item in items:
            result = cls.process_item(
                item.get('name', ''),
                item.get('description', ''),
                item.get('condition')
            )
            result['original'] = item
            results.append(result)
        return results
