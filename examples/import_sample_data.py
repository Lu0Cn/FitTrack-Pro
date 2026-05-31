"""
FitTrack Pro 示例数据导入脚本

此脚本用于将示例数据导入到 FitTrack Pro 数据库中。
注意：运行此脚本会清空现有数据并导入示例数据。

使用方法：
    python examples/import_sample_data.py
"""

import sys
import os
import json
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database as db

def import_sample_data():
    """导入示例数据到数据库"""
    
    print("=" * 50)
    print("FitTrack Pro 示例数据导入工具")
    print("=" * 50)
    print()
    
    # 确认操作
    confirm = input("⚠️  警告：此操作会清空现有数据并导入示例数据！\n是否继续？(yes/no): ")
    if confirm.lower() != 'yes':
        print("操作已取消。")
        return
    
    # 初始化数据库
    print("\n1. 初始化数据库...")
    db.init_db()
    print("   ✓ 数据库初始化完成")
    
    # 导入用户资料
    print("\n2. 导入用户资料...")
    try:
        with open(os.path.join(os.path.dirname(__file__), 'sample_user_profile.json'), 'r', encoding='utf-8') as f:
            profile_data = json.load(f)
            profile = profile_data['user_profile']
            
            db.save_user_profile(
                name=profile['name'],
                gender=profile['gender'],
                birth_date=profile['birth_date'],
                height=profile['height'],
                current_weight=profile['current_weight'],
                target_weight=profile['target_weight'],
                activity_level=profile['activity_level'],
                deepseek_api_key=profile['deepseek_api_key']
            )
            print(f"   ✓ 用户资料已导入：{profile['name']}")
    except Exception as e:
        print(f"   ✗ 导入用户资料失败：{e}")
    
    # 导入体重记录
    print("\n3. 导入体重记录...")
    try:
        with open(os.path.join(os.path.dirname(__file__), 'sample_weight_logs.json'), 'r', encoding='utf-8') as f:
            weight_data = json.load(f)
            count = 0
            for log in weight_data['weight_logs']:
                db.add_weight_log(
                    date=log['date'],
                    weight=log['weight'],
                    body_fat=log.get('body_fat'),
                    muscle_rate=log.get('muscle_rate'),
                    note=log.get('note', '')
                )
                count += 1
            print(f"   ✓ 已导入 {count} 条体重记录")
    except Exception as e:
        print(f"   ✗ 导入体重记录失败：{e}")
    
    # 导入饮食记录
    print("\n4. 导入饮食记录...")
    try:
        with open(os.path.join(os.path.dirname(__file__), 'sample_food_logs.json'), 'r', encoding='utf-8') as f:
            food_data = json.load(f)
            count = 0
            for log in food_data['food_logs']:
                db.add_food_log(
                    date=log['date'],
                    time=log['time'],
                    food_name=log['food_name'],
                    calories=log['calories'],
                    protein=log['protein'],
                    carbs=log['carbs'],
                    fat=log['fat'],
                    note=log.get('note', '')
                )
                count += 1
            print(f"   ✓ 已导入 {count} 条饮食记录")
    except Exception as e:
        print(f"   ✗ 导入饮食记录失败：{e}")
    
    # 导入运动记录
    print("\n5. 导入运动记录...")
    try:
        with open(os.path.join(os.path.dirname(__file__), 'sample_exercise_logs.json'), 'r', encoding='utf-8') as f:
            exercise_data = json.load(f)
            count = 0
            for log in exercise_data['exercise_logs']:
                db.add_exercise_log(
                    date=log['date'],
                    exercise_type=log['exercise_type'],
                    duration=log['duration_minutes'],
                    calories=log['calories_burned'],
                    note=log.get('note', '')
                )
                count += 1
            print(f"   ✓ 已导入 {count} 条运动记录")
    except Exception as e:
        print(f"   ✗ 导入运动记录失败：{e}")
    
    # 导入日常指标
    print("\n6. 导入日常指标...")
    try:
        with open(os.path.join(os.path.dirname(__file__), 'sample_daily_metrics.json'), 'r', encoding='utf-8') as f:
            metrics_data = json.load(f)
            count = 0
            for log in metrics_data['daily_metrics']:
                db.update_daily_metrics(
                    date=log['date'],
                    sleep=log['sleep_hours'],
                    water=log['water_ml'],
                    mood=log['mood_score'],
                    stress=log['stress_level']
                )
                count += 1
            print(f"   ✓ 已导入 {count} 条日常指标记录")
    except Exception as e:
        print(f"   ✗ 导入日常指标失败：{e}")
    
    print("\n" + "=" * 50)
    print("✅ 示例数据导入完成！")
    print("=" * 50)
    print("\n现在您可以：")
    print("1. 运行应用：streamlit run app.py")
    print("2. 查看仪表盘中的数据")
    print("3. 查看分析页面的图表")
    print("4. 体验 AI 功能（需要配置 API 密钥）")
    print()

if __name__ == '__main__':
    import_sample_data()

