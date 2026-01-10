import { contextBridge } from 'electron';
import { createElectronAPI } from './api';

// Create the unified API by combining all domain-specific APIs
const electronAPI = createElectronAPI();

// Expose to renderer via contextBridge
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

// Also expose as 'apex' for components using the apex namespace
contextBridge.exposeInMainWorld('apex', electronAPI);

// Expose debug flag for debug logging
contextBridge.exposeInMainWorld('DEBUG', process.env.DEBUG === 'true');