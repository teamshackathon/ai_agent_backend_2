# ai_agent_backend_2

```
ai_agent_backend_2/
│
├── app/                           # アプリケーションコード
│   ├── __init__.py
│   ├── api/                       # API関連
│   │   ├── __init__.py
│   │   ├── dependencies/          # 依存関係（認証ミドルウェアなど）
│   │   │   ├── __init__.py
│   │   │   └── auth.py           # 認証関連の依存関係
│   │   └── v1/                    # API Version 1
│   │       ├── __init__.py
│   │       ├── api.py             # API router登録
│   │       └── endpoints/         # エンドポイント定義
│   │           ├── __init__.py
│   │           ├── auth.py        # 認証エンドポイント
│   │           ├── users.py       # ユーザー関連エンドポイント
│   │           ├── chat.py        # チャットエンドポイント
│   │           └── healthcheck.py # ヘルスチェックエンドポイント
│   │
│   ├── core/                      # コア機能・設定
│   │   ├── __init__.py
│   │   ├── config.py              # 設定読み込み
│   │   ├── security.py            # セキュリティ関連
│   │   └── firebase_utils.py      # Firebase関連ユーティリティ
│   │
│   ├── models/                    # データモデル
│   │   ├── __init__.py
│   │   └── user.py                # ユーザーモデル
│   │
│   ├── schemas/                   # Pydanticスキーマ
│   │   ├── __init__.py
│   │   ├── auth.py                # 認証関連スキーマ
│   │   ├── chat.py                # チャット関連スキーマ
│   │   ├── base.py                # ベーススキーマ
│   │   └── user.py                # ユーザー関連スキーマ
│   │
│   └── services/                  # ビジネスロジック
│       ├── __init__.py
│       ├── auth_service.py        # 認証サービス
│       ├── chat_service.py        # チャットサービス
│       ├── user_service.py        # ユーザーサービス
│       ├── chain/                 # LangChain関連
│       │   ├── __init__.py
│       │   ├── base.py            # ベースチェーン
│       │   ├── dependency.py      # チェーン依存関係
│       │   └── pydantic_chain.py  # Pydanticチェーン
│       └── llm/                   # LLM関連
│           ├── __init__.py
│           └── gemini_client.py   # Geminiクライアント
│
├── tests/                         # テスト
│   ├── __init__.py
│   ├── conftest.py                # テスト共通設定
│   ├── api/                       # APIテスト
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   └── test_users.py
│   └── services/                  # サービステスト
│       ├── __init__.py
│       ├── test_auth_service.py
│       └── test_user_service.py
│
├── k8s/                           # Kubernetes設定
│   ├── deployment.yaml
│   └── service.yaml
│
├── .env.example                   # 環境変数のサンプル
├── .env.development               # 開発環境用設定
├── .gitignore
├── docker-compose.yaml            # 開発環境用Docker Compose
├── Dockerfile                     # プロダクション用Dockerfile
├── Dockerfile.dev                 # 開発用Dockerfile
├── main.py                        # アプリケーションエントリーポイント
├── pyproject.toml                 # プロジェクト設定
├── README.md
└── requirements.txt
```


バックエンドAPI統合ガイド: Firebase認証とGitHub OAuth
フロントエンド開発者向けに、バックエンドAPIとの連携方法をまとめました。

## 1. 開発環境セットアップ
バックエンドサーバーは以下の設定で動作しています:
- URL: http://localhost:8000
- API Base Path: /api/v1

### 環境変数設定
```bash
# Google API Key for Gemini
GOOGLE_API_KEY=your_google_api_key_here

# Other environment variables
OPENAPI_URL=
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

## 2. 認証フロー
### GitHub OAuth認証
1. **認証開始**: ユーザーを以下のURLにリダイレクト
   ```
   GET /api/v1/auth/github/login
   ```

2. **コールバック処理**:
   - GitHubから`http://localhost:8000/api/v1/auth/github/callback`にリダイレクト
   - バックエンドはユーザー情報を取得して処理
   - 最終的に`http://localhost:3000/auth/callback?token={custom_token}`にリダイレクト

3. **フロントエンド処理**:
   - URLからカスタムトークン(token)を取得
   - Firebase Authentication SDKを使用してサインイン

### Firebase認証の検証
1. **トークン検証**:
   ```
   POST /api/v1/auth/verify
   Content-Type: application/json
   {
     "id_token": "Firebase IdToken"
   }
   ```

2. **ユーザー情報取得**:
   ```
   GET /api/v1/auth/me
   Authorization: Bearer {Firebase IdToken}
   ```

## 3. チャット機能
### チャットエンドポイント
Gemini LLMを使用したチャット機能を提供します。

```
POST /api/v1/chat
Content-Type: application/json
{
  "role": "user",
  "response": "Hello, how are you?",
  "history": [
    {
      "role": "user",
      "content": "Previous message"
    },
    {
      "role": "assistant", 
      "content": "Previous response"
    }
  ],
  "model_name": "gemini-pro"  // Optional
}
```

**レスポンス**:
```json
{
  "role": "assistant",
  "response": "I'm doing well, thank you for asking! How can I help you today?"
}
```

### チャット機能の特徴
- **LangChain統合**: PydanticChainを使用した構造化された出力
- **リトライ機能**: レート制限エラー時の自動リトライ
- **履歴管理**: 会話履歴を考慮した応答生成
- **エラーハンドリング**: 適切なエラーレスポンス