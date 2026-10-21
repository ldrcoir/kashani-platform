package ir.science.platform;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebSettings;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.view.View;
import android.widget.TextView;
import android.content.Context;

public class MainActivity extends Activity {
    private WebView webView;
    private TextView offlineView;
    private static final String SITE_URL = "https://your-domain.com";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        webView = findViewById(R.id.webview);
        offlineView = findViewById(R.id.offline_view);
        
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setAllowFileAccess(true);
        settings.setSupportZoom(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onReceivedError(WebView view, int errorCode, String desc, String url) {
                showOffline();
            }
        });
        
        webView.setWebChromeClient(new WebChromeClient());
        
        if (isOnline()) {
            webView.loadUrl(SITE_URL);
            webView.setVisibility(View.VISIBLE);
            offlineView.setVisibility(View.GONE);
        } else {
            showOffline();
        }
    }
    
    private void showOffline() {
        webView.setVisibility(View.GONE);
        offlineView.setVisibility(View.VISIBLE);
        offlineView.setText("📱 برای استفاده از اپ نیاز به اتصال اینترنت دارید.\n\n⚠️ محتوای آفلاین نمایش داده نمی‌شود.\n\n لطفاً اینترنت را وصل کنید و دوباره باز کنید.");
    }
    
    private boolean isOnline() {
        ConnectivityManager cm = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo info = cm.getActiveNetworkInfo();
        return info != null && info.isConnected();
    }
    
    @Override
    public void onBackPressed() {
        if (webView.canGoBack() && webView.getVisibility() == View.VISIBLE) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
