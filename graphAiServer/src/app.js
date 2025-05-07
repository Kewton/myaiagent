// app.js
import express from 'express'; // require を import に変更
import { test, main as runGraphAiSample } from './services/sample.ts'; // 名前付きインポートとエイリアス
import dotenv from 'dotenv';
dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

// JSON ボディを解析するミドルウェアを追加
app.use(express.json());

app.get('/', (req, res) => {
  res.send('Hello Yarn Express!');
});

// ルートハンドラを async に変更
app.get('/test', async (req, res) => {
    try {
      console.log("Executing GraphAI sample...");
      const result = await test(); // await で完了を待つ
      console.log("GraphAI sample finished.");
      res.send(result);
    } catch (error) {
      console.error("Error executing GraphAI sample:", error);
      res.status(500).send('An error occurred while executing the GraphAI sample.');
    }
  });

// ルートハンドラを async に変更
app.post('/agent/sample', async (req, res) => {
  const { user_input,  model_name} = req.body;
  if (!user_input) {
    return res.status(400).json({ error: 'user_input は必須です' });
  }

  try {
    const result = await runGraphAiSample(user_input, model_name); // await で完了を待つ
    res.json(result);
  } catch (error) {
    console.error("Error executing GraphAI sample:", error);
    res.status(500).json({ error: 'An error occurred while executing the GraphAI sample.' });
  }
});


app.listen(port, () => {
  console.log(`サーバーがポート ${port} で起動しました: http://localhost:${port}`);
});