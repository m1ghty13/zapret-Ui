// Type declarations for pywebview API
interface PyWebViewAPI {
  browse_file(): Promise<string>;
  browse_folder(): Promise<string>;
  get_version(): Promise<string>;
  open_logs_folder(): Promise<boolean>;
}

interface Window {
  pywebview?: {
    api: PyWebViewAPI;
  };
}
