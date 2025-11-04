import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def setup_database():
    """创建SQLite数据库并生成模拟数据"""
    
    print("🚀 开始设置数据库...")
    
    # 连接SQLite数据库（会自动创建文件）
    conn = sqlite3.connect('logistics.db')
    cursor = conn.cursor()
    
    # 创建站点表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sites (
            site_id TEXT PRIMARY KEY,
            site_name TEXT NOT NULL,
            manager TEXT,
            region TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建配送记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS delivery_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            site_id TEXT NOT NULL,
            rider_id TEXT,
            rider_name TEXT,
            total_orders INTEGER NOT NULL,
            completed_orders INTEGER NOT NULL,
            rejected_orders INTEGER NOT NULL,
            on_time_orders INTEGER NOT NULL,
            total_cost REAL NOT NULL,
            delivery_hours INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 清空现有数据
    cursor.execute('DELETE FROM sites')
    cursor.execute('DELETE FROM delivery_records')
    
    # 插入美国站点数据
    sites = [
        ('site_la', '洛杉矶市中心站', 'John Smith', '加州'),
        ('site_ny', '纽约曼哈顿站', 'Mike Johnson', '纽约'), 
        ('site_sf', '旧金山站', 'David Wilson', '加州'),
        ('site_chi', '芝加哥站', 'Robert Brown', '伊利诺伊'),
        ('site_mia', '迈阿密站', 'James Davis', '佛罗里达'),
        ('site_sea', '西雅图站', 'William Miller', '华盛顿')
    ]
    
    # 美国配送员信息
    riders = {
        'site_la': ['Rider_LA01-John', 'Rider_LA02-Mike', 'Rider_LA03-Tom'],
        'site_ny': ['Rider_NY01-Robert', 'Rider_NY02-Kevin', 'Rider_NY03-Brian'],
        'site_sf': ['Rider_SF01-Chris', 'Rider_SF02-Jason', 'Rider_SF03-Eric'],
        'site_chi': ['Rider_CHI01-Steve', 'Rider_CHI02-Paul', 'Rider_CHI03-Mark'],
        'site_mia': ['Rider_MIA01-Daniel', 'Rider_MIA02-Anthony', 'Rider_MIA03-Jose'],
        'site_sea': ['Rider_SEA01-Ryan', 'Rider_SEA02-Jeffrey', 'Rider_SEA03-Gary']
    }
    
    cursor.executemany('INSERT INTO sites VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)', sites)
    
    # 生成30天的模拟数据
    delivery_data = []
    for day in range(30, 0, -1):
        current_date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
        
        for site_id, site_name, manager, region in sites:
            for rider_name in riders[site_id]:
                rider_id = rider_name.split('-')[0]  # 提取骑手ID
                
                # 模拟每日订单量（美国订单量可能更多）
                total_orders = np.random.randint(25, 60)  # 每个骑手的订单
                completed_orders = int(total_orders * np.random.uniform(0.92, 0.98))
                rejected_orders = int(total_orders * np.random.uniform(0.01, 0.05))
                on_time_orders = int(completed_orders * np.random.uniform(0.88, 0.96))
                total_cost = round(np.random.uniform(300, 600), 2)  # 美元成本
                delivery_hours = np.random.randint(6, 10)  # 工作时长
                
                delivery_data.append((
                    current_date, site_id, rider_id, rider_name, total_orders, 
                    completed_orders, rejected_orders, on_time_orders, total_cost, 
                    delivery_hours
                ))
    
    # 插入配送数据
    cursor.executemany('''
        INSERT INTO delivery_records 
        (date, site_id, rider_id, rider_name, total_orders, completed_orders, 
         rejected_orders, on_time_orders, total_cost, delivery_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', delivery_data)
    
    conn.commit()
    
    # 验证数据
    cursor.execute('SELECT COUNT(*) FROM delivery_records')
    record_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM sites')
    site_count = cursor.fetchone()[0]
    
    print(f"✅ 数据库设置完成！")
    print(f"📊 站点数量: {site_count}")
    print(f"📈 配送记录: {record_count} 条")
    print(f"💾 数据库文件: logistics.db")
    
    # 显示示例数据
    print(f"\n📋 数据示例:")
    cursor.execute('''
        SELECT date, site_id, rider_name, total_orders, 
               ROUND(completed_orders * 100.0 / total_orders, 2) as completion_rate,
               ROUND(rejected_orders * 100.0 / total_orders, 2) as rejection_rate,
               ROUND(on_time_orders * 100.0 / total_orders, 2) as on_time_rate
        FROM delivery_records 
        ORDER BY date DESC 
        LIMIT 5
    ''')
    
    for row in cursor.fetchall():
        print(f"   {row[0]} | {row[1]} | {row[2]} | 订单:{row[3]} | 完成率:{row[4]}% | 拒收率:{row[5]}% | 准时率:{row[6]}%")
    
    conn.close()

if __name__ == "__main__":
    setup_database()