import streamlit as st
import pandas as pd
import csv
import io
from datetime import datetime, timedelta
import time

# スタッツの種類を定義（HTML/CSSでスタイリング）
STATS_FIELDS = [
    "shoot in","goal","shoot out",
    "pass suc","assist","pass failed",
    "steal the ball","lost the ball",
    "saved_gk","conceded_gk"
]

# スタッツの表示名とカラーを定義
STATS_COLORS = {
    "shoot in": "#FF4B4B",
    "goal": "#FF4B4B",
    "shoot out": "#FF4B4B",
    "pass suc": "#1E90FF",
    "assist": "#1E90FF",
    "pass failed": "#1E90FF",
    "steal the ball": "#FFD700",
    "lost the ball": "#8B4513",
    "saved_gk": "#4169E1",
    "conceded_gk": "#4169E1"
}

def colored_header(text, color):
    st.markdown(f'<h4 style="color: {color};">{text}</h4>', unsafe_allow_html=True)

def init_timer():
    if 'time_remaining' not in st.session_state:
        st.session_state.time_remaining = 10 * 60
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    if 'custom_time' not in st.session_state:
        st.session_state.custom_time = 10

def format_time(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

def main():
    st.title("選手スタッツ記録システム")

    # タイマーと試合情報を左サイドバーに配置
    with st.sidebar:
        st.header("試合情報")
        match_date = st.date_input("試合日", value=datetime.now())
        opponent = st.text_input("対戦相手")
        
        st.header("タイマー設定")
        st.write("※ 以下修正対応中")
        init_timer()
        
        # 時間設定
        half = st.radio("時間区分", ["前半", "後半", "一本"], horizontal=True)
        custom_minutes = st.number_input(
            "試合時間（分）",
            min_value=1,
            max_value=90,
            value=st.session_state.custom_time
        )
        
        if st.button("時間をセット"):
            st.session_state.time_remaining = custom_minutes * 60
            st.session_state.custom_time = custom_minutes
            st.session_state.timer_running = False

        # タイマーコントロール
        col1, col2 = st.columns(2)
        with col1:
            if st.button(("停止" if st.session_state.timer_running else "開始")):
                st.session_state.timer_running = not st.session_state.timer_running
        with col2:
            if st.button("リセット"):
                st.session_state.time_remaining = st.session_state.custom_time * 60
                st.session_state.timer_running = False
        
        # タイマー表示
        time_display = format_time(st.session_state.time_remaining)
        st.markdown(
            f"""
            <div style="
                padding: 20px;
                background-color: #f0f2f6;
                border-radius: 10px;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
            ">
                ⏱️ {time_display}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if st.session_state.timer_running and st.session_state.time_remaining > 0:
            time.sleep(1)
            st.session_state.time_remaining -= 1
            st.rerun()

    # メインコンテンツ
    uploaded_file = st.file_uploader("メンバーリスト(CSV)をアップロード", type=['csv'])
    
    if uploaded_file is not None:
        members_df = pd.read_csv(uploaded_file)
        
        if 'stats' not in st.session_state:
            st.session_state.stats = {}
            for _, row in members_df.iterrows():
                st.session_state.stats[row['名前']] = {field: 0 for field in STATS_FIELDS}

        st.subheader("スタッツ記録")
        tabs = st.tabs(STATS_FIELDS)
        for tab, stat in zip(tabs, STATS_FIELDS):
            with tab:
                colored_header(stat, STATS_COLORS[stat])
                for name in members_df['名前']:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"{name}: {st.session_state.stats[name][stat]}")
                    with col2:
                        if st.button("+1", key=f"plus_{name}_{stat}"):
                            st.session_state.stats[name][stat] += 1
                            st.rerun()
                    with col3:
                        if st.button("-1", key=f"minus_{name}_{stat}"):
                            if st.session_state.stats[name][stat] > 0:
                                st.session_state.stats[name][stat] -= 1
                                st.rerun()

        # 全データの表示（タブの外に移動）
        st.write("---")
        st.subheader("全選手データ一覧")
        
        # 表示用データフレーム（試合情報なし）
        stats_data_display = []
        for name in members_df['名前'].tolist():
            row_data = {
                '名前': name
            }
            # スタッツデータを追加
            for stat in STATS_FIELDS:
                row_data[stat] = st.session_state.stats[name][stat]
            stats_data_display.append(row_data)
        
        # 表示用データフレーム
        df_display = pd.DataFrame(stats_data_display)
        st.dataframe(df_display, use_container_width=True)

        # 保存用データフレーム（試合情報を含む）
        stats_data_save = []
        for name in members_df['名前'].tolist():
            row_data = {
                '試合日': match_date.strftime('%Y-%m-%d'),
                '対戦相手': opponent,
                'ハーフ': half,
                '名前': name
            }
            # スタッツデータを追加
            for stat in STATS_FIELDS:
                row_data[stat] = st.session_state.stats[name][stat]
            stats_data_save.append(row_data)
        
        # 保存用データフレーム（表示しない）
        df_save = pd.DataFrame(stats_data_save)

        # CSVダウンロードボタン（保存用データフレームを使用）
        csv_data = df_save.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 スタッツデータをダウンロード",
            data=csv_data,
            file_name=f"選手スタッツ_{match_date.strftime('%Y%m%d')}_{opponent}.csv",
            mime="text/csv",
            use_container_width=True
        )

if __name__ == "__main__":
    main()
    
