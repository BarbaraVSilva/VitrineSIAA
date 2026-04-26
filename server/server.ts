import express, { Request, Response } from "express";
import { createServer as createViteServer } from "vite";
import path from "path";
import { fileURLToPath } from "url";
import admin from "firebase-admin";
// @ts-ignore
import firebaseConfig from "./firebase-applet-config.json" assert { type: "json" };
import { spawn } from "child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootPath = path.join(__dirname, "..");

// Initialize Firebase Admin
if (!admin.apps.length) {
  admin.initializeApp({
    projectId: firebaseConfig.projectId,
  });
}

// @ts-ignore
const db = admin.firestore();

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // API Routes
  app.get("/api/health", (_req: Request, res: Response) => {
    res.json({ status: "ok", firebase: "connected" });
  });

  // Bridge to Python Scraper
  app.post("/api/scrape/shopee", (req: Request, res: Response) => {
    const { url } = req.body;
    if (!url) return res.status(400).json({ error: "URL is required" });

    console.log(`[Bridge] Starting Shopee scraper for: ${url}`);
    
    const pythonProcess = spawn("python", [
      "-c", 
      `import sys; import os; sys.path.append(os.path.join(os.getcwd(), 'backend')); from app.mineracao.shopee_scraper import scrape_shopee_data; from app.core.firebase_sync import firebase_sync; import json; res = scrape_shopee_data('${url}'); res['source'] = 'Manual Search'; item_id = firebase_sync.push_mining_item(res); print(json.dumps({'id': item_id, 'data': res}))`
    ], {
      cwd: rootPath
    });

    let output = "";
    pythonProcess.stdout.on("data", (data: Buffer) => {
      output += data.toString();
    });

    pythonProcess.stderr.on("data", (data: Buffer) => {
      console.error(`[Python Error] ${data}`);
    });

    pythonProcess.on("close", (code: number) => {
      if (code === 0) {
        try {
          const result = JSON.parse(output.split("\n").filter(l => l.trim().startsWith("{")).pop() || "{}");
          res.json({ success: true, ...result });
        } catch (e) {
          res.json({ success: true, message: "Scraped successfully but output parsing failed.", raw: output });
        }
      } else {
        res.status(500).json({ error: "Python process failed", code });
      }
    });
  });

  // Bridge to Vitrine Updater
  app.post("/api/vitrine/update", (_req: Request, res: Response) => {
    console.log("[Bridge] Triggering Vitrine Update...");
    
    const pythonProcess = spawn("python", [
      "backend/app/publisher/update_vitrine.py"
    ], {
      cwd: rootPath
    });

    pythonProcess.stdout.on("data", (data: Buffer) => {
      console.log(`[Vitrine] ${data}`);
    });

    pythonProcess.stderr.on("data", (data: Buffer) => {
      console.error(`[Vitrine Error] ${data}`);
    });

    res.json({ success: true, message: "Vitrine update triggered" });
  });

  // Bridge to Video Processor
  app.post("/api/process/video", (req: Request, res: Response) => {
    const { videoPath, productName, productDesc, price, productId } = req.body;
    if (!videoPath || !productId) return res.status(400).json({ error: "Missing required fields" });

    const taskId = `task_${Date.now()}`;
    console.log(`[Bridge] Starting Video Pipeline for task: ${taskId}`);
    
    const pythonProcess = spawn("python", [
      "-c", 
      `import sys; import os; sys.path.append(os.path.join(os.getcwd(), 'backend')); from app.mineracao.video_pipeline import run_5_videos_pipeline; run_5_videos_pipeline('${videoPath.replace(/\\/g, '/')}', '${productName}', '${productDesc}', '${price}', ${productId}, '${taskId}')`
    ], {
      cwd: rootPath
    });

    pythonProcess.stderr.on("data", (data: Buffer) => {
      console.error(`[Python Video Error] ${data}`);
    });

    res.json({ success: true, taskId });
  });

  // Vite middleware for development (pointing to frontend/)
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      root: path.join(rootPath, "frontend"),
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(rootPath, "frontend", "dist");
    app.use(express.static(distPath));
    app.get("*", (_req: Request, res: Response) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Unified Server running on http://localhost:${PORT}`);
  });
}

startServer();
