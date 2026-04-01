"""
时空约束匹配服务
用于匹配买卖双方的可交易时间和地点，并生成可执行的面交建议。
"""
from datetime import datetime
import re


class TimeLocationService:
    """时空匹配服务"""

    LOCATION_PROFILES = {
        '图书馆': {
            'aliases': ['主图书馆', '图书馆门口', '图书馆前', '图书馆附近', '自习室'],
            'tags': ['academic', 'quiet', 'central', 'public'],
            'public_score': 10,
            'central_score': 9
        },
        '食堂': {
            'aliases': ['餐厅', '饭堂', '食堂门口', '食堂附近', '学生食堂'],
            'tags': ['living', 'central', 'public', 'daily'],
            'public_score': 10,
            'central_score': 8
        },
        '宿舍楼': {
            'aliases': ['宿舍', '寝室楼', '公寓', '生活区'],
            'tags': ['living', 'private', 'daily'],
            'public_score': 4,
            'central_score': 4
        },
        '教学楼': {
            'aliases': ['教学区', '教学楼下', '教室楼', '教学楼门口'],
            'tags': ['academic', 'public', 'central'],
            'public_score': 8,
            'central_score': 8
        },
        '体育馆': {
            'aliases': ['体育中心', '球馆', '健身馆'],
            'tags': ['sports', 'public'],
            'public_score': 7,
            'central_score': 5
        },
        '操场': {
            'aliases': ['运动场', '田径场'],
            'tags': ['sports', 'public', 'open'],
            'public_score': 7,
            'central_score': 5
        },
        '校门口': {
            'aliases': ['校门', '南门', '北门', '东门', '西门', '校门附近'],
            'tags': ['transit', 'public', 'central'],
            'public_score': 9,
            'central_score': 7
        },
        '超市': {
            'aliases': ['便利店', '商店', '生活超市'],
            'tags': ['living', 'daily', 'public'],
            'public_score': 8,
            'central_score': 6
        },
        '咖啡厅': {
            'aliases': ['咖啡店', '饮品店', '奶茶店'],
            'tags': ['social', 'quiet', 'public', 'central'],
            'public_score': 9,
            'central_score': 7
        },
        '快递站': {
            'aliases': ['快递点', '驿站', '菜鸟驿站', '快递柜'],
            'tags': ['living', 'transit', 'daily', 'public'],
            'public_score': 8,
            'central_score': 6
        }
    }

    # 预定义的常用地点
    COMMON_LOCATIONS = list(LOCATION_PROFILES.keys())

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

    WEEKDAY_NAMES = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    PUBLIC_FALLBACK_LOCATIONS = ['图书馆', '食堂', '校门口', '咖啡厅']

    @staticmethod
    def _clean_text(text):
        if text is None:
            return ''
        return re.sub(r'[\s,，、/()（）\-]+', '', str(text).strip())

    @staticmethod
    def _minutes_to_hhmm(minutes):
        hours = minutes // 60
        mins = minutes % 60
        return f'{hours:02d}:{mins:02d}'

    @staticmethod
    def _round_score(score):
        return max(0, min(100, int(round(score))))

    @classmethod
    def normalize_location(cls, location):
        """
        将地点名称归一化到统一的校园地点类型。
        例如“主图书馆门口”会被映射为“图书馆”。
        """
        raw = str(location or '').strip()
        if not raw:
            return None

        clean = cls._clean_text(raw)
        for canonical, profile in cls.LOCATION_PROFILES.items():
            aliases = [canonical] + profile.get('aliases', [])
            for alias in aliases:
                alias_clean = cls._clean_text(alias)
                if not alias_clean:
                    continue
                if clean == alias_clean or alias_clean in clean or clean in alias_clean:
                    return canonical
        return raw

    @classmethod
    def _get_location_profile(cls, location):
        canonical = cls.normalize_location(location)
        profile = cls.LOCATION_PROFILES.get(canonical, {})
        return canonical, {
            'tags': set(profile.get('tags', [])),
            'public_score': profile.get('public_score', 6),
            'central_score': profile.get('central_score', 5)
        }

    @classmethod
    def _normalize_location_list(cls, locations):
        normalized = []
        seen = set()
        for location in locations or []:
            canonical = cls.normalize_location(location)
            if canonical and canonical not in seen:
                normalized.append(canonical)
                seen.add(canonical)
        return normalized

    @staticmethod
    def parse_time_slot(time_slot_str):
        """
        解析时间段字符串
        例如: "周一 08:00-12:00"
        """
        weekday_map = {
            '周一': 0, '周二': 1, '周三': 2, '周四': 3,
            '周五': 4, '周六': 5, '周日': 6
        }

        pattern = r'(周[一二三四五六日])\s+(\d{2}:\d{2})-(\d{2}:\d{2})'
        match = re.match(pattern, str(time_slot_str or '').strip())
        if not match:
            return None

        weekday_str, start_time, end_time = match.groups()
        start_minutes = int(start_time[:2]) * 60 + int(start_time[3:])
        end_minutes = int(end_time[:2]) * 60 + int(end_time[3:])
        if start_minutes >= end_minutes:
            return None

        weekday = weekday_map.get(weekday_str)
        return {
            'weekday': weekday,
            'start': start_time,
            'end': end_time,
            'start_minutes': start_minutes,
            'end_minutes': end_minutes,
            'duration_minutes': end_minutes - start_minutes,
            'original': f'{weekday_str} {start_time}-{end_time}'
        }

    @classmethod
    def _days_ahead(cls, weekday):
        now = datetime.now()
        return (weekday - now.weekday()) % 7

    @classmethod
    def _parse_time_slots(cls, time_slots):
        parsed = []
        seen = set()
        for slot in time_slots or []:
            parsed_slot = cls.parse_time_slot(slot)
            if not parsed_slot:
                continue
            key = parsed_slot['original']
            if key in seen:
                continue
            seen.add(key)
            parsed.append(parsed_slot)
        parsed.sort(key=lambda x: (cls._days_ahead(x['weekday']), x['start_minutes']))
        return parsed

    @classmethod
    def _build_exact_time_candidates(cls, buyer_slots, seller_slots):
        candidates = []
        seen = set()

        for buyer_slot in buyer_slots:
            for seller_slot in seller_slots:
                if buyer_slot['weekday'] != seller_slot['weekday']:
                    continue

                overlap_start = max(buyer_slot['start_minutes'], seller_slot['start_minutes'])
                overlap_end = min(buyer_slot['end_minutes'], seller_slot['end_minutes'])
                if overlap_start >= overlap_end:
                    continue

                duration = overlap_end - overlap_start
                days_ahead = cls._days_ahead(buyer_slot['weekday'])
                label = (
                    f"{cls.WEEKDAY_NAMES[buyer_slot['weekday']]} "
                    f"{cls._minutes_to_hhmm(overlap_start)}-{cls._minutes_to_hhmm(overlap_end)}"
                )
                if label in seen:
                    continue
                seen.add(label)

                duration_score = min(1.0, duration / 120.0)
                recency_score = max(0.2, 1 - days_ahead / 7.0)
                score = 55 + duration_score * 25 + recency_score * 20

                candidates.append({
                    'label': label,
                    'score': cls._round_score(score),
                    'exact_match': True,
                    'duration_minutes': duration,
                    'gap_minutes': 0,
                    'days_ahead': days_ahead,
                    'reason': f'双方在该时段都可交易，重叠时长约 {duration} 分钟'
                })

        candidates.sort(key=lambda x: (-x['score'], x['days_ahead'], -x['duration_minutes']))
        return candidates

    @classmethod
    def _build_negotiation_time_candidates(cls, buyer_slots, seller_slots):
        candidates = []
        seen = set()

        for buyer_slot in buyer_slots:
            for seller_slot in seller_slots:
                if buyer_slot['weekday'] != seller_slot['weekday']:
                    continue

                gap = None
                anchor_minutes = None
                if buyer_slot['end_minutes'] <= seller_slot['start_minutes']:
                    gap = seller_slot['start_minutes'] - buyer_slot['end_minutes']
                    anchor_minutes = seller_slot['start_minutes']
                elif seller_slot['end_minutes'] <= buyer_slot['start_minutes']:
                    gap = buyer_slot['start_minutes'] - seller_slot['end_minutes']
                    anchor_minutes = buyer_slot['start_minutes']

                if gap is None or gap > 180:
                    continue

                days_ahead = cls._days_ahead(buyer_slot['weekday'])
                label = f"{cls.WEEKDAY_NAMES[buyer_slot['weekday']]} {cls._minutes_to_hhmm(anchor_minutes)} 左右"
                if label in seen:
                    continue
                seen.add(label)

                closeness_score = max(0.0, 1 - gap / 180.0)
                recency_score = max(0.2, 1 - days_ahead / 7.0)
                score = 35 + closeness_score * 30 + recency_score * 10
                reason = (
                    f'双方当天时间接近，但仍相差约 {gap} 分钟，'
                    f'建议优先协商 {cls._minutes_to_hhmm(anchor_minutes)} 左右面交'
                )

                candidates.append({
                    'label': label,
                    'score': cls._round_score(score),
                    'exact_match': False,
                    'duration_minutes': 0,
                    'gap_minutes': gap,
                    'days_ahead': days_ahead,
                    'reason': reason
                })

        candidates.sort(key=lambda x: (-x['score'], x['days_ahead'], x['gap_minutes']))
        return candidates

    @classmethod
    def _build_directional_time_candidates(cls, known_slots, owner_label):
        candidates = []
        for slot in known_slots[:3]:
            days_ahead = cls._days_ahead(slot['weekday'])
            recency_score = max(0.2, 1 - days_ahead / 7.0)
            duration_score = min(1.0, slot['duration_minutes'] / 180.0)
            score = 28 + recency_score * 12 + duration_score * 10
            candidates.append({
                'label': slot['original'],
                'score': cls._round_score(score),
                'exact_match': False,
                'duration_minutes': slot['duration_minutes'],
                'gap_minutes': None,
                'days_ahead': days_ahead,
                'reason': f'{owner_label}已设置该时间，可优先围绕这个时段沟通'
            })
        return candidates

    @classmethod
    def get_time_candidates(cls, buyer_time_slots, seller_time_slots):
        buyer_slots = cls._parse_time_slots(buyer_time_slots)
        seller_slots = cls._parse_time_slots(seller_time_slots)

        if buyer_slots and seller_slots:
            exact_candidates = cls._build_exact_time_candidates(buyer_slots, seller_slots)
            if exact_candidates:
                return exact_candidates
            return cls._build_negotiation_time_candidates(buyer_slots, seller_slots)

        if buyer_slots:
            return cls._build_directional_time_candidates(buyer_slots, '你')

        if seller_slots:
            return cls._build_directional_time_candidates(seller_slots, '卖家')

        return []

    @classmethod
    def find_common_time_slots(cls, slots1, slots2):
        return [candidate['label'] for candidate in cls._build_exact_time_candidates(
            cls._parse_time_slots(slots1),
            cls._parse_time_slots(slots2)
        )]

    @classmethod
    def _location_similarity(cls, location_a, location_b):
        canonical_a, profile_a = cls._get_location_profile(location_a)
        canonical_b, profile_b = cls._get_location_profile(location_b)
        if not canonical_a or not canonical_b:
            return 0.0
        if canonical_a == canonical_b:
            return 1.0

        tags_a = profile_a['tags']
        tags_b = profile_b['tags']
        union = tags_a | tags_b
        jaccard = (len(tags_a & tags_b) / len(union)) if union else 0.0
        public_score = min(profile_a['public_score'], profile_b['public_score']) / 10.0
        central_score = 1 - abs(profile_a['central_score'] - profile_b['central_score']) / 10.0

        similarity = 0.55 * jaccard + 0.20 * public_score + 0.25 * central_score
        return max(0.0, min(0.95, similarity))

    @classmethod
    def find_common_locations(cls, locs1, locs2):
        set1 = set(cls._normalize_location_list(locs1))
        set2 = set(cls._normalize_location_list(locs2))
        return list(set1 & set2)

    @classmethod
    def _build_location_reason(cls, candidate, buyer_locations, seller_locations):
        location = candidate['location']
        if location in buyer_locations and location in seller_locations:
            return '买卖双方地点偏好一致，适合直接约在这里面交'
        if candidate['buyer_similarity'] >= 0.75 and candidate['seller_similarity'] >= 0.75:
            return '与双方常用区域都比较接近，适合作为折中面交点'
        if candidate['buyer_similarity'] >= 0.75:
            return '更贴近你的常用地点，同时卖家接受度也较高'
        if candidate['seller_similarity'] >= 0.75:
            return '更贴近卖家的常用地点，通常更容易约成'
        return '属于公共区域，安全性和可达性更好，适合作为协商地点'

    @classmethod
    def get_location_candidates(cls, buyer_locations, seller_locations):
        buyer_norm = cls._normalize_location_list(buyer_locations)
        seller_norm = cls._normalize_location_list(seller_locations)

        if not buyer_norm and not seller_norm:
            return []

        candidate_pool = []
        seen = set()
        for location in buyer_norm + seller_norm + cls.PUBLIC_FALLBACK_LOCATIONS:
            if location and location not in seen:
                candidate_pool.append(location)
                seen.add(location)

        candidates = []
        for location in candidate_pool:
            _, profile = cls._get_location_profile(location)

            if buyer_norm:
                buyer_similarity = max(cls._location_similarity(location, buyer_loc) for buyer_loc in buyer_norm)
            else:
                buyer_similarity = profile['public_score'] / 12.0

            if seller_norm:
                seller_similarity = max(cls._location_similarity(location, seller_loc) for seller_loc in seller_norm)
            else:
                seller_similarity = profile['public_score'] / 12.0

            exact_match = location in buyer_norm and location in seller_norm
            public_bonus = profile['public_score'] / 10.0 * 8
            central_bonus = profile['central_score'] / 10.0 * 6
            score = buyer_similarity * 42 + seller_similarity * 42 + public_bonus + central_bonus
            if exact_match:
                score += 8

            if max(buyer_similarity, seller_similarity) < 0.45 and not exact_match:
                continue

            candidate = {
                'location': location,
                'score': cls._round_score(score),
                'exact_match': exact_match,
                'buyer_similarity': round(buyer_similarity, 3),
                'seller_similarity': round(seller_similarity, 3)
            }
            candidate['reason'] = cls._build_location_reason(candidate, buyer_norm, seller_norm)
            candidates.append(candidate)

        candidates.sort(
            key=lambda x: (
                -x['score'],
                not x['exact_match'],
                -x['buyer_similarity'],
                -x['seller_similarity']
            )
        )
        return candidates[:5]

    @classmethod
    def calculate_match_score(cls, time_candidates, location_candidates):
        if not time_candidates and not location_candidates:
            return 0, 0, 0

        time_score = time_candidates[0]['score'] if time_candidates else 0
        location_score = location_candidates[0]['score'] if location_candidates else 0

        total = time_score * 0.55 + location_score * 0.45
        if time_candidates and location_candidates:
            if time_candidates[0]['exact_match'] and location_candidates[0]['exact_match']:
                total += 8
            elif time_candidates[0]['exact_match'] or location_candidates[0]['exact_match']:
                total += 4
        return (
            cls._round_score(total),
            cls._round_score(time_score),
            cls._round_score(location_score)
        )

    @classmethod
    def _build_message(cls, exact_match, best_time, best_location, missing_time, missing_location):
        if missing_time and missing_location:
            return '你还没有设置常用时间和地点，系统先按卖家信息给出建议'
        if exact_match:
            return '时间和地点都比较契合，可以直接发消息确认面交'
        if best_time and best_location:
            return '已为你找到最接近的面交方案，建议优先按下方方案与卖家沟通'
        if best_time:
            return '时间上较接近，但地点还需要和卖家再确认'
        if best_location:
            return '地点上有较优选择，但时间还需要和卖家进一步协商'
        return '暂时无法给出明确方案，建议先补充偏好后再尝试匹配'

    @classmethod
    def _build_action_plan(cls, best_time, best_location, exact_match):
        time_label = best_time['label'] if best_time else None
        location_label = best_location['location'] if best_location else None

        if time_label and location_label:
            if exact_match:
                return f'推荐优先约在 {time_label}，地点选 {location_label}。'
            return f'建议优先协商 {time_label}，如双方方便，可在 {location_label} 面交。'
        if time_label:
            return f'建议先围绕 {time_label} 和卖家确认具体见面地点。'
        if location_label:
            return f'建议优先把面交地点定在 {location_label}，再与卖家确认具体时间。'
        return '建议先在个人中心补充交易偏好，再重新查看匹配结果。'

    @classmethod
    def _build_profile_tips(cls, missing_time, missing_location):
        tips = []
        if missing_time:
            tips.append('补充常用交易时间后，系统能更准确地推荐可面交时段')
        if missing_location:
            tips.append('补充常用交易地点后，系统能推荐更合适的面交点')
        return tips

    @classmethod
    def get_match_suggestions(cls, buyer_time_slots, buyer_locations,
                              seller_time_slots, seller_locations):
        """
        获取匹配建议
        """
        buyer_time_slots = buyer_time_slots or []
        buyer_locations = buyer_locations or []
        seller_time_slots = seller_time_slots or []
        seller_locations = seller_locations or []

        time_candidates = cls.get_time_candidates(buyer_time_slots, seller_time_slots)
        location_candidates = cls.get_location_candidates(buyer_locations, seller_locations)
        common_time_slots = cls.find_common_time_slots(buyer_time_slots, seller_time_slots)
        common_locations = cls.find_common_locations(buyer_locations, seller_locations)

        best_time = time_candidates[0] if time_candidates else None
        best_location = location_candidates[0] if location_candidates else None
        exact_match = bool(common_time_slots and common_locations)
        has_match = bool(best_time and best_location)
        match_score, time_score, location_score = cls.calculate_match_score(
            time_candidates, location_candidates
        )

        if match_score >= 80:
            match_level = 'high'
        elif match_score >= 60:
            match_level = 'medium'
        elif match_score >= 40:
            match_level = 'low'
        else:
            match_level = 'very_low'

        missing_time = len(buyer_time_slots) == 0
        missing_location = len(buyer_locations) == 0
        message = cls._build_message(
            exact_match, best_time, best_location, missing_time, missing_location
        )
        action_plan = cls._build_action_plan(best_time, best_location, exact_match)

        return {
            'match_score': match_score,
            'time_score': time_score,
            'location_score': location_score,
            'match_level': match_level,
            'has_match': has_match,
            'exact_match': exact_match,
            'buyer_missing_time_preferences': missing_time,
            'buyer_missing_location_preferences': missing_location,
            'profile_completion_tips': cls._build_profile_tips(missing_time, missing_location),
            'common_time_slots': common_time_slots,
            'common_locations': common_locations,
            'best_time_label': best_time['label'] if best_time else None,
            'best_time_slot': best_time['label'] if best_time and best_time['exact_match'] else None,
            'best_time_exact': bool(best_time and best_time['exact_match']),
            'best_time_reason': best_time['reason'] if best_time else None,
            'best_location': best_location['location'] if best_location else None,
            'best_location_exact': bool(best_location and best_location['exact_match']),
            'best_location_reason': best_location['reason'] if best_location else None,
            'time_candidates': time_candidates[:3],
            'location_candidates': location_candidates[:3],
            'message': message,
            'action_plan': action_plan
        }

    @staticmethod
    def validate_time_slot(time_slot_str):
        """验证时间段格式是否正确"""
        parsed = TimeLocationService.parse_time_slot(time_slot_str)
        return parsed is not None

    @classmethod
    def get_next_available_time(cls, time_slots):
        """
        获取下一个可用的时间段
        """
        parsed_slots = cls._parse_time_slots(time_slots)
        if not parsed_slots:
            return None

        next_slot = parsed_slots[0]
        days_ahead = cls._days_ahead(next_slot['weekday'])
        return {
            'time_slot': next_slot['original'],
            'days_ahead': days_ahead if days_ahead > 0 else 0,
            'is_today': days_ahead == 0
        }
