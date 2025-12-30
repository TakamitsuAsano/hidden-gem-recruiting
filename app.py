import streamlit as st
import google.generativeai as genai
import os

# --- ページ設定 ---
st.set_page_config(
    page_title="Hidden Gem Recruiter 💎",
    page_icon="💎",
    layout="wide"
)

# --- サイドバー：設定 ---
st.sidebar.title("💎 設定 / Settings")
st.sidebar.markdown("Gemini API Keyを入力してください。")

# APIキーの入力（セキュアに入力）
api_key = st.sidebar.text_input("Google Gemini API Key", type="password")
model_name = "gemini-1.5-flash" # コスト効率重視

# --- メインエリア ---
st.title("💎 Hidden Gem Recruiting: Canvas Prompt Generator")
st.markdown("""
地域の企業や宇宙ベンチャーの「埋もれた魅力」を発掘し、
Gemini Canvasで**「刺さる求人サイト」**を一発生成するためのプロンプト作成ツールです。
""")

st.divider()

# --- Step 1: ターゲットとモード設定 ---
st.header("Step 1: 採用モードの定義")

col1, col2 = st.columns(2)

with col1:
    client_name = st.text_input("クライアント企業名", placeholder="例：株式会社コスモテック")
    target_audience = st.text_input("メインターゲット（ペルソナ）", placeholder="例：30代の組み込みエンジニア、Uターン希望者")

with col2:
    mode = st.radio(
        "採用モード（Focus Selector）",
        ("Corporate Base (全社・理念重視)", 
         "Specific Project (プロジェクト・ミッション重視)", 
         "Regional/Local (地域・生活重視)", 
         "Skill/Tech (技術・環境重視)"),
        help="どの切り口で求人サイトを作るか選択してください。"
    )

# --- Step 2: 素材の入力（ごった煮） ---
st.header("Step 2: 素材データ入力（非構造化データ）")
st.caption("ヒアリングの文字起こし、資料のテキスト、既存サイトの文言などをそのまま貼り付けてください。")

input_tab1, input_tab2, input_tab3 = st.tabs(["🗣️ ヒアリング (Transcript)", "📄 資料/スライド (Docs)", "🌐 既存サイト/Web (Current Info)"])

with input_tab1:
    text_transcript = st.text_area("インタビュー・会話ログ", height=200, placeholder="社長や現場社員との会話ログを貼り付け...")
with input_tab2:
    text_docs = st.text_area("会社資料・PPT等のテキスト", height=200, placeholder="会社案内や求人票のテキストを貼り付け...")
with input_tab3:
    text_web = st.text_area("既存Webサイト情報", height=200, placeholder="現在のHPにある沿革や事業内容などを貼り付け...")

# 全テキストを結合
raw_data = f"""
【ヒアリング情報】
{text_transcript}

【資料情報】
{text_docs}

【既存Web情報】
{text_web}
"""

# --- Step 3: プロンプト生成ロジック ---
st.divider()
generate_btn = st.button("🚀 Canvas用プロンプトを生成する", type="primary")

if generate_btn:
    if not api_key:
        st.error("左側のサイドバーでAPI Keyを設定してください。")
    elif not raw_data.strip():
        st.warning("素材データが入力されていません。")
    else:
        try:
            # Geminiの設定
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)

            # --- メタ・プロンプトの構築（ここが肝） ---
            # 選択されたモードに応じた「重視すべきポイント」の定義
            focus_instruction = ""
            if "Specific Project" in mode:
                focus_instruction = """
                - **最重要視点:** 「期間限定」「ミッションの緊急性」「成功時の社会的インパクト」。
                - **抽出方針:** ワクワクする挑戦の要素、プロジェクトの詳細、期限、解決すべき課題を抜き出す。
                - **デザイン指示:** LP形式。映画の予告編のような高揚感。ヒーローセクションを大きく。
                """
            elif "Regional/Local" in mode:
                focus_instruction = """
                - **最重要視点:** 「ライフスタイル」「働く環境」「地域コミュニティとの関わり」。
                - **抽出方針:** オフィスの雰囲気、周辺環境、UIターンのメリット、社員の笑顔や人間関係を抜き出す。
                - **デザイン指示:** マガジン形式。写真を多用し、空気感や安心感を伝えるグリッドレイアウト。
                """
            elif "Skill/Tech" in mode:
                focus_instruction = """
                - **最重要視点:** 「技術スタック」「開発環境」「エンジニアリングカルチャー」「裁量権」。
                - **抽出方針:** 使用言語、ツール、開発手法、技術的な課題の難易度、キャリアパスを詳細に抜き出す。
                - **デザイン指示:** ドキュメント/スペックシート形式。ダークモード基調、情報の網羅性と検索性を重視。
                """
            else: # Corporate Base
                focus_instruction = """
                - **最重要視点:** 「創業の想い」「企業の歴史」「ビジョン」「安定性と成長性」。
                - **抽出方針:** 創業ストーリー、代表の哲学、福利厚生、全社的な文化をバランスよく抜き出す。
                - **デザイン指示:** コーポレートサイト形式。信頼感、誠実さ、洗練された印象。
                """

            # LLMへの命令（メタ・プロンプト）
            system_prompt = f"""
            あなたはプロの「求人サイト構成作家」です。
            以下の「雑多な入力データ」を分析し、Google Gemini Canvas（Webサイト生成AI）に入力するための
            『最高品質の指示プロンプト』を作成してください。

            ## 対象クライアント
            企業名: {client_name}
            ターゲット: {target_audience}
            採用モード: {mode}

            ## あなたのタスク
            1. 入力データから、上記の「採用モード」に最適な「Hidden Gems（埋もれた魅力）」を発掘・抽出してください。
            2. それ以外のノイズ（無関係な情報）は捨ててください。
            3. Gemini Canvasに対して、「HTML/Tailwind CSSでサイトを出力せよ」という命令文を構成してください。

            ## 採用モードごとの指針
            {focus_instruction}

            ## 出力フォーマット（この形式で出力してください）
            ---
            あなたは世界最高峰のWebデザイナー兼コピーライターです。
            以下の情報を元に、{target_audience}の心を動かす採用Webサイト（HTMLシングルページ + Tailwind CSS）を作成してください。

            ### 1. サイトのコンセプト
            （ここに、抽出した魅力を元にしたサイトのコンセプトを記載）

            ### 2. 掲載すべき主要コンテンツ（Context）
            （入力データから抽出した、事実・ストーリー・数値を構造化して記載）
            - キャッチコピー案: ...
            - 必須セクション: ...
            - 魅力の根拠: ...

            ### 3. デザインとトーン＆マナー
            （採用モードに基づいた具体的なデザイン指示）
            - 配色: ...
            - レイアウト: ...
            - 雰囲気: ...

            ### 4. 実装要件
            - HTML5, Tailwind CSS (CDN)を使用
            - 画像はプレースホルダー (https://placehold.co/...) を使用
            - レスポンシブ対応
            - 実際にブラウザで動作するコードを出力すること
            ---
            """

            with st.spinner('💎 魅力を抽出中... Geminiが思考しています...'):
                response = model.generate_content([system_prompt, raw_data])
                generated_prompt = response.text

            # --- 結果表示 ---
            st.success("✅ プロンプト生成完了！")
            st.markdown("以下のテキストをコピーして、**Gemini Canvas** に貼り付けてください。")
            
            st.code(generated_prompt, language="markdown")
            
            st.info("💡 Tip: Canvasで出力されたサイトを見ながら、「もっと写真を大きく」「セクションを入れ替えて」と会話で修正してください。")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")