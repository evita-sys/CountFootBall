import streamlit as st
import pandas as pd
import datetime
import csv

def save_to_csv(data):
    with open('soccer_members.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(data)

def check_duplicate_number(number, members, current_name=None):
    for member in members:
        if member['背番号'] == number and member['名前'] != current_name:
            return True
    return False

def main():
    st.title("登録システム")

    # セッション状態の初期化
    if 'members' not in st.session_state:
        st.session_state.members = []

    # フォームの作成
    with st.form("member_registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("名前")
        
        with col2:
            jersey_number = st.number_input("背番号", min_value=1, max_value=99)

        submitted = st.form_submit_button("登録")

        if submitted:
            if name:  # 名前が入力されているか確認
                # 背番号の重複チェック
                if check_duplicate_number(jersey_number, st.session_state.members):
                    st.error(f"背番号 {jersey_number} は既に使用されています")
                else:
                    # メンバー情報を辞書として保存
                    member = {
                        "名前": name,
                        "背番号": jersey_number,
                    }
                    
                    # セッションステートに追加
                    st.session_state.members.append(member)
                    
                    # CSVファイルに保存
                    save_to_csv([name, jersey_number])
                    
                    st.success(f"{name}を登録")
            else:
                st.error("名前を入力してください。")

    # 登録メンバーの表示
    if st.session_state.members:
        st.subheader("登録メンバー一覧")
        df = pd.DataFrame(st.session_state.members)
        st.dataframe(df)

        # CSVダウンロードボタン
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="メンバーリストダウンロード",
            data=csv,
            file_name="soccer_members.csv",
            mime="text/csv"
        )

        st.write('===================================-')

        # メンバー削除機能
        st.subheader("メンバー削除")
        if len(st.session_state.members) > 0:
            delete_name = st.selectbox(
                "削除するメンバーを選択",
                options=[member["名前"] for member in st.session_state.members]
            )
            if st.button("削除"):
                # 選択されたメンバーを削除
                st.session_state.members = [
                    member for member in st.session_state.members 
                    if member["名前"] != delete_name
                ]
                st.success(f"{delete_name}を削除しました")
                st.rerun()



if __name__ == "__main__":
    main()
