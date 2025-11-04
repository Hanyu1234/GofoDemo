from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.orm import Session
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

from database import engine, get_db, Base

# 定义数据模型
class DeliveryRecord(Base):
    __tablename__ = "delivery_records"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    site_id = Column(String(50), index=True)
    rider_id = Column(String(50))
    rider_name = Column(String(100))  # 新增字段
    total_orders = Column(Integer)
    completed_orders = Column(Integer)
    rejected_orders = Column(Integer)
    on_time_orders = Column(Integer)
    total_cost = Column(Float)
    delivery_hours = Column(Integer)  # 新增字段：工作时长
    
class Site(Base):
    __tablename__ = "sites"
    
    site_id = Column(String(50), primary_key=True, index=True)
    site_name = Column(String(100))
    manager = Column(String(50))
    region = Column(String(50))

# 创建表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="物流看板系统", description="物流运营数据监控平台")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "物流看板系统API"}

@app.get("/api/kpi/daily")
async def get_daily_kpi(
    start_date: str,
    end_date: str,
    site_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # 查询数据
    query = db.query(
        DeliveryRecord.date,
        DeliveryRecord.site_id,
        DeliveryRecord.total_orders,
        DeliveryRecord.completed_orders,
        DeliveryRecord.rejected_orders,
        DeliveryRecord.on_time_orders,
        DeliveryRecord.total_cost
    ).filter(
        DeliveryRecord.date >= start_date,
        DeliveryRecord.date <= end_date
    )
    
    if site_id:
        query = query.filter(DeliveryRecord.site_id == site_id)
    
    records = query.all()
    
    if not records:
        return []
    
    # 转换为DataFrame
    df = pd.DataFrame([{
        'date': r.date,
        'site_id': r.site_id,
        'total_orders': r.total_orders,
        'completed_orders': r.completed_orders,
        'rejected_orders': r.rejected_orders,
        'on_time_orders': r.on_time_orders,
        'total_cost': r.total_cost
    } for r in records])
    
    # 计算KPI
    daily_kpis = df.groupby('date').agg({
        'total_orders': 'sum',
        'completed_orders': 'sum',
        'rejected_orders': 'sum',
        'on_time_orders': 'sum',
        'total_cost': 'sum'
    }).reset_index()
    
    daily_kpis['completion_rate'] = (daily_kpis['completed_orders'] / daily_kpis['total_orders'] * 100).round(2)
    daily_kpis['rejection_rate'] = (daily_kpis['rejected_orders'] / daily_kpis['total_orders'] * 100).round(2)
    daily_kpis['eta_achievement_rate'] = (daily_kpis['on_time_orders'] / daily_kpis['total_orders'] * 100).round(2)
    daily_kpis['cost_per_order'] = (daily_kpis['total_cost'] / daily_kpis['total_orders']).round(2)
    
    return daily_kpis.to_dict('records')

@app.get("/api/kpi/sites")
async def get_site_performance(
    date: str,
    db: Session = Depends(get_db)
):
    records = db.query(DeliveryRecord).filter(DeliveryRecord.date == date).all()
    
    if not records:
        return []
    
    df = pd.DataFrame([{
        'site_id': r.site_id,
        'total_orders': r.total_orders,
        'completed_orders': r.completed_orders,
        'rejected_orders': r.rejected_orders,
        'on_time_orders': r.on_time_orders
    } for r in records])
    
    site_perf = df.groupby('site_id').agg({
        'total_orders': 'sum',
        'completed_orders': 'sum',
        'rejected_orders': 'sum',
        'on_time_orders': 'sum'
    }).reset_index()
    
    site_perf['completion_rate'] = (site_perf['completed_orders'] / site_perf['total_orders'] * 100).round(2)
    site_perf['rejection_rate'] = (site_perf['rejected_orders'] / site_perf['total_orders'] * 100).round(2)
    site_perf['eta_achievement_rate'] = (site_perf['on_time_orders'] / site_perf['total_orders'] * 100).round(2)
    
    # 添加状态
    def get_status(row):
        if row['completion_rate'] < 97 or row['rejection_rate'] > 2.5:
            return 'exception'
        elif row['completion_rate'] < 98 or row['rejection_rate'] > 1.5:
            return 'warning'
        else:
            return 'normal'
    
    site_perf['status'] = site_perf.apply(get_status, axis=1)
    
    return site_perf.to_dict('records')

@app.get("/api/sites/list")
async def get_sites_list(db: Session = Depends(get_db)):
    """获取所有站点列表"""
    sites = db.query(Site).all()
    return [{
        'site_id': site.site_id,
        'site_name': site.site_name,
        'manager': site.manager,
        'region': site.region
    } for site in sites]

@app.get("/api/riders/performance")
async def get_rider_performance(
    date: str,
    site_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取配送员绩效数据"""
    query = db.query(
        DeliveryRecord.rider_id,
        DeliveryRecord.rider_name,
        DeliveryRecord.site_id,
        DeliveryRecord.total_orders,
        DeliveryRecord.completed_orders,
        DeliveryRecord.rejected_orders,
        DeliveryRecord.on_time_orders,
        DeliveryRecord.total_cost,
        DeliveryRecord.delivery_hours
    ).filter(DeliveryRecord.date == date)
    
    if site_id:
        query = query.filter(DeliveryRecord.site_id == site_id)
    
    records = query.all()
    
    if not records:
        return []
    
    # 计算配送员KPI
    rider_data = []
    for record in records:
        completion_rate = round((record.completed_orders / record.total_orders) * 100, 2) if record.total_orders > 0 else 0
        rejection_rate = round((record.rejected_orders / record.total_orders) * 100, 2) if record.total_orders > 0 else 0
        on_time_rate = round((record.on_time_orders / record.total_orders) * 100, 2) if record.total_orders > 0 else 0
        cost_per_order = round(record.total_cost / record.total_orders, 2) if record.total_orders > 0 else 0
        orders_per_hour = round(record.total_orders / record.delivery_hours, 2) if record.delivery_hours > 0 else 0
        
        rider_data.append({
            'rider_id': record.rider_id,
            'rider_name': record.rider_name,
            'site_id': record.site_id,
            'total_orders': record.total_orders,
            'completed_orders': record.completed_orders,
            'rejected_orders': record.rejected_orders,
            'on_time_orders': record.on_time_orders,
            'completion_rate': completion_rate,
            'rejection_rate': rejection_rate,
            'on_time_rate': on_time_rate,
            'cost_per_order': cost_per_order,
            'delivery_hours': record.delivery_hours,
            'orders_per_hour': orders_per_hour,
            'total_cost': record.total_cost
        })
    
    return rider_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    

@app.get("/api/riders/performance")
async def get_rider_performance(
    date: str,
    site_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取配送员绩效数据"""
    query = db.query(
        DeliveryRecord.rider_id,
        DeliveryRecord.rider_name,
        DeliveryRecord.site_id,
        DeliveryRecord.total_orders,
        DeliveryRecord.completed_orders,
        DeliveryRecord.rejected_orders,
        DeliveryRecord.on_time_orders,
        DeliveryRecord.total_cost,
        DeliveryRecord.delivery_hours
    ).filter(DeliveryRecord.date == date)
    
    if site_id:
        query = query.filter(DeliveryRecord.site_id == site_id)
    
    records = query.all()
    
    if not records:
        return []
    
    # 计算配送员KPI
    rider_data = []
    for record in records:
        completion_rate = round((record.completed_orders / record.total_orders) * 100, 2) if record.total_orders > 0 else 0
        rejection_rate = round((record.rejected_orders / record.total_orders) * 100, 2) if record.total_orders > 0 else 0
        on_time_rate = round((record.on_time_orders / record.total_orders) * 100, 2) if record.total_orders > 0 else 0
        cost_per_order = round(record.total_cost / record.total_orders, 2) if record.total_orders > 0 else 0
        orders_per_hour = round(record.total_orders / record.delivery_hours, 2) if record.delivery_hours > 0 else 0
        
        rider_data.append({
            'rider_id': record.rider_id,
            'rider_name': record.rider_name,
            'site_id': record.site_id,
            'total_orders': record.total_orders,
            'completed_orders': record.completed_orders,
            'rejected_orders': record.rejected_orders,
            'on_time_orders': record.on_time_orders,
            'completion_rate': completion_rate,
            'rejection_rate': rejection_rate,
            'on_time_rate': on_time_rate,
            'cost_per_order': cost_per_order,
            'delivery_hours': record.delivery_hours,
            'orders_per_hour': orders_per_hour,
            'total_cost': record.total_cost
        })
    
    return rider_data

@app.get("/api/sites/list")
async def get_sites_list(db: Session = Depends(get_db)):
    """获取所有站点列表"""
    sites = db.query(Site).all()
    return [{
        'site_id': site.site_id,
        'site_name': site.site_name,
        'manager': site.manager,
        'region': site.region
    } for site in sites]