// Holography Bench — Electron shell around the WebGPU simulator (src/index.html).
const { app, BrowserWindow, Menu, shell, dialog } = require("electron");
const path = require("path");

// WebGPU: make sure it is on even for GPUs/drivers that Chromium has not yet allow-listed.
// The page's own start-up check verifies the results against the CPU code before anything is used.
app.commandLine.appendSwitch("enable-unsafe-webgpu");
app.commandLine.appendSwitch("force_high_performance_gpu");   // prefer the discrete GPU on dual-GPU laptops

let win = null;
function createWindow() {
  win = new BrowserWindow({
    width: 1500, height: 960, minWidth: 900, minHeight: 600,
    backgroundColor: "#161b21", title: "Holography Bench", show: false,
    icon: path.join(__dirname, "build", "icon.png"),
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true, spellcheck: false }
  });
  win.loadFile(path.join(__dirname, "site", "index.html"));
  win.once("ready-to-show", () => win.show());
  // keep all navigation inside the app; open real web links in the default browser
  win.webContents.setWindowOpenHandler(({ url }) => { if (/^https?:/.test(url)) shell.openExternal(url); return { action: "deny" }; });
  win.webContents.on("will-navigate", (e, url) => { if (!url.startsWith("file:")) { e.preventDefault(); if (/^https?:/.test(url)) shell.openExternal(url); } });
}

function gpuReport() {
  const w = new BrowserWindow({ width: 1000, height: 800, title: "GPU report", autoHideMenuBar: true });
  w.loadURL("chrome://gpu");
}

const template = [
  { label: "File", submenu: [
    { label: "Restart simulator", accelerator: "CmdOrCtrl+R", click: () => win && win.reload() },
    { type: "separator" }, { role: "quit" } ] },
  { label: "View", submenu: [
    { role: "zoomIn" }, { role: "zoomOut" }, { role: "resetZoom" }, { type: "separator" },
    { role: "togglefullscreen" }, { type: "separator" },
    { label: "Developer tools", accelerator: "F12", click: () => win && win.webContents.toggleDevTools() } ] },
  { label: "Help", submenu: [
    { label: "GPU report (chrome://gpu)", click: gpuReport },
    { label: "About", click: () => dialog.showMessageBox(win, { type: "info", title: "About Holography Bench",
      message: `Holography Bench ${app.getVersion()}`,
      detail: `Simulators for in-line (lensless) and off-axis digital holographic microscopy.\n\nElectron ${process.versions.electron} · Chromium ${process.versions.chrome}` }) } ] }
];

app.whenReady().then(() => {
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
  createWindow();
  app.on("activate", () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});
app.on("window-all-closed", () => { if (process.platform !== "darwin") app.quit(); });
