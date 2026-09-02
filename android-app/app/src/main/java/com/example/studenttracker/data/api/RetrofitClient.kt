package com.example.studenttracker.data.api

import android.content.Context
import com.example.studenttracker.utils.Constants
import com.example.studenttracker.utils.SessionManager
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {

    private var apiService: ApiService? = null

    fun getApiService(context: Context): ApiService {
        if (apiService == null) {
            val sessionManager = SessionManager(context)

            val authInterceptor = Interceptor { chain ->
                val original = chain.request()
                val requestBuilder = original.newBuilder()

                val token = sessionManager.getAuthToken()
                if (!token.isNullOrEmpty()) {
                    requestBuilder.header("Authorization", "Bearer $token")
                }

                requestBuilder.header("Accept", "application/json")
                chain.proceed(requestBuilder.build())
            }

            val loggingInterceptor = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }

            val okHttpClient = OkHttpClient.Builder()
                .addInterceptor(authInterceptor)
                .addInterceptor(loggingInterceptor)
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .build()

            val retrofit = Retrofit.Builder()
                .baseUrl(Constants.BASE_URL)
                .client(okHttpClient)
                .addConverterFactory(GsonConverterFactory.create())
                .build()

            apiService = retrofit.create(ApiService::class.java)
        }
        return apiService!!
    }
}
