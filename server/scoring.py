"""
评分算法实现
"""
import math
from datetime import date, datetime


def calculate_score(votes: int, last_commit_date: date) -> dict:
    """
    计算烂尾指数

    Args:
        votes: 投票数
        last_commit_date: 最后提交日期

    Returns:
        {
            'votes': 投票数,
            'days_stale': 停更天数,
            'vote_score': 投票分数 (0-60),
            'stale_score': 停更分数 (0-40),
            'total_score': 总分 (0-100)
        }
    """
    # 计算停更天数
    today = date.today()
    days_stale = (today - last_commit_date).days

    # 投票分数：V = min(60, round(20 * log2(1 + votes)))
    vote_score = min(60, round(20 * math.log2(1 + votes)))

    # 停更分数：S = min(40, floor(days_since_last_commit / 7))
    stale_score = min(40, days_stale // 7)

    # 总分：min(100, V + S)
    total_score = min(100, vote_score + stale_score)

    return {
        'votes': votes,
        'days_stale': days_stale,
        'vote_score': vote_score,
        'stale_score': stale_score,
        'total_score': total_score
    }


def score(votes: int, last_commit_date: date) -> int:
    """
    快捷方法：直接返回总分

    Args:
        votes: 投票数
        last_commit_date: 最后提交日期

    Returns:
        总分 (0-100)
    """
    return calculate_score(votes, last_commit_date)['total_score']
