package com.tracker.studentmanagement

import android.annotation.SuppressLint
import android.graphics.Bitmap
import android.os.Bundle
import android.view.View
import android.webkit.*
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var swipeRefreshLayout: SwipeRefreshLayout

    // Default backend REST API URL (Live Vercel Cloud Server)
    private var appUrl = "https://student-management-system-alpha-liard.vercel.app"

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Dynamic view setup
        swipeRefreshLayout = SwipeRefreshLayout(this)
        webView = WebView(this)
        swipeRefreshLayout.addView(webView)
        setContentView(swipeRefreshLayout)

        // Enable JavaScript and modern Web APIs
        val webSettings = webView.settings
        webSettings.javaScriptEnabled = true
        webSettings.domStorageEnabled = true
        webSettings.databaseEnabled = true
        webSettings.loadWithOverviewMode = false
        webSettings.useWideViewPort = false
        webSettings.allowFileAccess = true
        webSettings.allowContentAccess = true
        webSettings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW

        // Setup WebView Clients
        webView.webViewClient = object : WebViewClient() {
            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                swipeRefreshLayout.isRefreshing = true
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                swipeRefreshLayout.isRefreshing = false
            }

            override fun onReceivedError(
                view: WebView?,
                errorCode: Int,
                description: String?,
                failingUrl: String?
            ) {
                swipeRefreshLayout.isRefreshing = false
                Toast.makeText(this@MainActivity, "Connection Note: $description", Toast.LENGTH_SHORT).show()
            }
        }

        webView.webChromeClient = WebChromeClient()

        // Pull to refresh action
        swipeRefreshLayout.setOnRefreshListener {
            webView.reload()
        }

        // Load Application
        webView.loadUrl(appUrl)
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
