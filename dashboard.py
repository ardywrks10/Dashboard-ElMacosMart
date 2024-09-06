import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  
import streamlit as st 
from babel.numbers import format_currency 
sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule = 'D', on = 'order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby(by="product_category_name").product_id.nunique().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    return bycity_df

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    return bystate_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "payment_value": "sum"
    })
    
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frekuensi", "moneter"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df

all_df = pd.read_csv('all_data.csv')

datetime_columns = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']
all_df.sort_values(by='order_purchase_timestamp', inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])
    
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    st.image("el_macos.png")
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df['order_purchase_timestamp'] >= str(start_date)) & 
                 (all_df['order_purchase_timestamp'] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bycity_df = create_bycity_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header("Dashboard El Macos Mart :sparkles:")

st.subheader("Pesanan Harian")

col1, col2 = st.columns(2)
with col1:
    total_order = daily_orders_df.order_count.sum()
    st.metric("Total pesanan: ", value=total_order)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale="es_CO")
    st.metric("Total penjualan: ", value=total_revenue)

fig, ax = plt.subplots(figsize=(18, 9))
ax.plot(
    daily_orders_df['order_purchase_timestamp'],
    daily_orders_df['order_count'],
    marker='o',
    linewidth=2,
    color='#90CAF9'
)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
ax.set_title("Jumlah Pesanan Harian", fontsize=20)
st.pyplot(fig)

st.markdown("<br><br>", unsafe_allow_html=True)

st.subheader("Kategori Produk dengan Penjualan Tertinggi dan Terendah")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
fig.subplots_adjust(wspace=0.4)  

sns.barplot(x='product_id', y='product_category_name', data=sum_order_items_df.head(5), palette="Blues_d", ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Jumlah Pesanan", fontsize=30)
ax[0].set_title("Kategori Produk Terlaris", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x='product_id', y='product_category_name', data=sum_order_items_df.sort_values(by="product_id", ascending=True).head(5), palette="Blues_d", ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Jumlah Pesanan", fontsize=30)
ax[1].set_title("Kategori Produk Terendah", loc="center", fontsize=50)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
st.pyplot(fig)

st.markdown("<br><br>", unsafe_allow_html=True)
st.subheader("Demografi Pelanggan")

fix, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
sns.barplot(x="customer_id", y="customer_city", data=bycity_df.sort_values(by="customer_id", ascending=False).head(5), palette="Blues_d", ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Jumlah Pesanan", fontsize=30)
ax[0].set_title ("Penjualan Berdasarkan Kota", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x='customer_id', y='customer_state', data=bystate_df.sort_values(by="customer_id", ascending=True).head(5), palette="Blues_d", ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Jumlah Pesanan", fontsize=30)
ax[1].set_title("Penjualan Berdasarkan Negara Bagian", loc="center", fontsize=50)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
st.pyplot(fix)

st.markdown("<br><br>", unsafe_allow_html=True)
st.subheader("Customer Terbaik Berdasarkan RFM Parameter")
col1, col2, col3 = st.columns(3)

with col1:
    recency = round(rfm_df["recency"].mean(), 1)
    st.metric("Recency Rata-rata (hari): ", value=recency)
with col2:
    frequency = round(rfm_df["frekuensi"].mean(), 1)
    st.metric("Frekuensi Rata-rata: ", value=frequency)
with col3:
    moneter = format_currency(rfm_df["moneter"].mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=moneter)
    
figs, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
top_10_rfm = rfm_df.head(10)
colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]
sns.barplot(y="recency", x="customer_id", hue="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0], legend=False)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Berdasarkan recency (hari)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15)
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45)

sns.barplot(y="moneter", x="customer_id", hue="customer_id", data=rfm_df.sort_values(by="moneter", ascending=False).head(5), palette=colors, ax=ax[1], legend=False)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("Berdasarkan Moneter ($)", loc="center", fontsize=18)
ax[1].tick_params(axis ='x', labelsize=15)
ax[1].set_xticklabels(ax[0].get_xticklabels(), rotation=45)

sns.barplot(y="frekuensi", x="customer_id", hue="customer_id", data=rfm_df.sort_values(by="frekuensi", ascending=False).head(5), palette=colors, ax=ax[2], legend=False)
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("Berdasarkan Frekuensi", loc="center", fontsize=18)
ax[2].tick_params(axis ='x', labelsize=15)
ax[2].set_xticklabels(ax[0].get_xticklabels(), rotation=45)
st.pyplot(figs)
    