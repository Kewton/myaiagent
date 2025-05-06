// app.js
import express from 'express'; // require を import に変更
import { main as runGraphAiSample } from './services/sample.ts'; // 名前付きインポートとエイリアス

const app = express();
const port = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.send('Hello Yarn Express!');
});

// ルートハンドラを async に変更
app.get('/test', async (req, res) => {
    try {
      console.log("Executing GraphAI sample...");
      const result = await runGraphAiSample(); // await で完了を待つ
      console.log("GraphAI sample finished.");
      res.send(result);
    } catch (error) {
      console.error("Error executing GraphAI sample:", error);
      res.status(500).send('An error occurred while executing the GraphAI sample.');
    }
  });

app.listen(port, () => {
  console.log(`サーバーがポート <span class="math-inline">\{port\} で起動しました\: http\://localhost\:</span>{port}`);
});