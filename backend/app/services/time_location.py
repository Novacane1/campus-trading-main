"""
时空约束匹配服务
用于匹配买卖双方的可交易时间和地点
"""
from datetime import datetime, timedelta
import re


class TimeLocationService:
    """时空匹配服务"""

    # 预定义的常用地点
    COMMON_LOCATIONS = [
        '图书馆', '食堂', '宿舍楼', '教学楼', '体育馆',
        '操场', '校门口', '超市', '咖啡厅', '快递站'
    ]

    # 预定义的时间段
    TIME_SLOTS = [
        '周一 08:00-12:00', '周一 14:00-18:00', '周一 19:00-21:00',
        '周二 08:00-12:00', '周二 14:00-18:00', '周二 19:00-21:00',
        '周三 08:00-12:00', '周三 14:00-18:00', '周三 19:00-21:00',
        '周四 08:00-12:00', '周四 14:00-18:00', '周四 19:00-21:00',
        '周五 08:00-12:00', '周五 14:00-18:00', '周五 19:00-21:00',
        '周六 08:00-12:00', '周六 14:00-18:00', '周六 19:00-21:00',
        '周日 08:00-12:00', '周日 14:00-18:00', '周日 19:00-21:00',
    ]

    @staticmethod
    def parse_time_slot(time_slot_str):
        """
        解析时间段字符串
        例如: "周一 08:00-12:00" -> {'weekday': 0, 'start': '08:00', 'end': '12:00'}
        """
        weekday_map = {
            '周一': 0, '周二': 1, '周三': 2, '周四': 3,
            '周五': 4, '周六': 5, '周日': 6
        }

        pattern = r'(周[一二三四五六日])\s+(\d{2}:\d{2})-(\d{2}:\d{2})'
        match = re.match(pattern, time_slot_str)

        if not match:
            return None

        weekday_str, start_time, end_time = match.groups()
        return {
            'weekday': weekday_map.get(weekday_str),
            'start': start_time,
            'end': end_time,
            'original': time_slot_str
        }

    @staticmethod
    def find_common_time_slots(slots1, slots2):
        """
        找出两个时间段列表的交集
        """
        if not slots1 or not slots2:
            return []

        parsed_slots1 = [TimeLocationService.parse_time_slot(s) for s in slots1]
        parsed_slots2 = [TimeLocationService.parse_time_slot(s) for s in slots2]

        # 过滤掉解析失败的
        parsed_slots1 = [s for s in parsed_slots1 if s]
        parsed_slots2 = [s for s in parsed_slots2 if s]

        common_slots = []

        for slot1 in parsed_slots1:
            for slot2 in parsed_slots2:
                # 检查是否同一天
                if slot1['weekday'] != slot2['weekday']:
                    continue

                # 检查时间是否有重叠
                start1 = datetime.strptime(slot1['start'], '%H:%M')
                end1 = datetime.strptime(slot1['end'], '%H:%M')
                start2 = datetime.strptime(slot2['start'], '%H:%M')
                end2 = datetime.strptime(slot2['end'], '%H:%M')

                # 计算重叠时间段
                overlap_start = max(start1, start2)
                overlap_end = min(end1, end2)

                if overlap_start < overlap_end:
                    weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
                    common_slot = f"{weekday_names[slot1['weekday']]} {overlap_start.strftime('%H:%M')}-{overlap_end.strftime('%H:%M')}"
                    if common_slot not in common_slots:
                        common_slots.append(common_slot)

        return common_slots

    @staticmethod
    def find_common_locations(locs1, locs2):
        """
        找出两个地点列表的交集
        """
        if not locs1 or not locs2:
            return []

        set1 = set(locs1)
        set2 = set(locs2)
        return list(set1 & set2)

    @staticmethod
    def calculate_match_score(buyer_time_slots, buyer_locations,
                             seller_time_slots, seller_locations):
        """
        计算买卖双方的时空匹配度
        返回 0-100 的分数
        """
        score = 0

        # 时间匹配度 (50分)
        common_time_slots = TimeLocationService.find_common_time_slots(
            buyer_time_slots, seller_time_slots
        )
        if common_time_slots:
            time_score = min(50, len(common_time_slots) * 10)
            score += time_score

        # 地点匹配度 (50分)
        common_locations = TimeLocationService.find_common_locations(
            buyer_locations, seller_locations
        )
        if common_locations:
            location_score = min(50, len(common_locations) * 15)
            score += location_score

        return score

    @staticmethod
    def get_match_suggestions(buyer_time_slots, buyer_locations,
                             seller_time_slots, seller_locations):
        """
        获取匹配建议
        """
        common_time_slots = TimeLocationService.find_common_time_slots(
            buyer_time_slots, seller_time_slots
        )
        common_locations = TimeLocationService.find_common_locations(
            buyer_locations, seller_locations
        )

        match_score = TimeLocationService.calculate_match_score(
            buyer_time_slots, buyer_locations,
            seller_time_slots, seller_locations
        )

        suggestions = {
            'match_score': match_score,
            'common_time_slots': common_time_slots,
            'common_locations': common_locations,
            'has_match': len(common_time_slots) > 0 and len(common_locations) > 0
        }

        # 生成建议文本
        if suggestions['has_match']:
            suggestions['message'] = f"找到 {len(common_time_slots)} 个可交易时间段和 {len(common_locations)} 个共同地点"
        elif common_time_slots:
            suggestions['message'] = "找到可交易时间，但没有共同地点，建议协商地点"
        elif common_locations:
            suggestions['message'] = "找到共同地点，但时间不匹配，建议协商时间"
        else:
            suggestions['message'] = "时间和地点都不匹配，建议双方协商"

        return suggestions

    @staticmethod
    def validate_time_slot(time_slot_str):
        """验证时间段格式是否正确"""
        parsed = TimeLocationService.parse_time_slot(time_slot_str)
        return parsed is not None

    @staticmethod
    def get_next_available_time(time_slots):
        """
        获取下一个可用的时间段
        """
        if not time_slots:
            return None

        now = datetime.now()
        current_weekday = now.weekday()
        current_time = now.time()

        for time_slot in time_slots:
            parsed = TimeLocationService.parse_time_slot(time_slot)
            if not parsed:
                continue

            slot_weekday = parsed['weekday']
            slot_start = datetime.strptime(parsed['start'], '%H:%M').time()

            # 计算距离现在的天数
            days_ahead = (slot_weekday - current_weekday) % 7

            if days_ahead == 0:
                # 今天的时间段
                if slot_start > current_time:
                    return {
                        'time_slot': time_slot,
                        'days_ahead': 0,
                        'is_today': True
                    }
            elif days_ahead > 0:
                return {
                    'time_slot': time_slot,
                    'days_ahead': days_ahead,
                    'is_today': False
                }

        # 如果没有找到，返回第一个时间段（下周）
        if time_slots:
            first_slot = TimeLocationService.parse_time_slot(time_slots[0])
            if first_slot:
                days_ahead = (first_slot['weekday'] - current_weekday + 7) % 7
                return {
                    'time_slot': time_slots[0],
                    'days_ahead': days_ahead if days_ahead > 0 else 7,
                    'is_today': False
                }

        return None
