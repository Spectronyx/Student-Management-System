package com.example.studenttracker.utils

import android.content.Context
import android.content.SharedPreferences

class SessionManager(context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences("academic_tracker_prefs", Context.MODE_PRIVATE)

    companion object {
        private const val KEY_AUTH_TOKEN = "auth_token"
        private const val KEY_USER_ID = "user_id"
        private const val KEY_ROLE_ID = "role_id"
        private const val KEY_USER_ROLE = "user_role"
        private const val KEY_USER_NAME = "user_name"
        private const val KEY_USER_EMAIL = "user_email"
    }

    fun saveAuthSession(token: String, userId: Int, roleId: Int, role: String, name: String, email: String) {
        prefs.edit().apply {
            putString(KEY_AUTH_TOKEN, token)
            putInt(KEY_USER_ID, userId)
            putInt(KEY_ROLE_ID, roleId)
            putString(KEY_USER_ROLE, role)
            putString(KEY_USER_NAME, name)
            putString(KEY_USER_EMAIL, email)
            apply()
        }
    }

    fun getAuthToken(): String? = prefs.getString(KEY_AUTH_TOKEN, null)
    fun getUserId(): Int = prefs.getInt(KEY_USER_ID, -1)
    fun getRoleId(): Int = prefs.getInt(KEY_ROLE_ID, -1)
    fun getUserRole(): String? = prefs.getString(KEY_USER_ROLE, null)
    fun getUserName(): String? = prefs.getString(KEY_USER_NAME, null)
    fun getUserEmail(): String? = prefs.getString(KEY_USER_EMAIL, null)

    fun isLoggedIn(): Boolean = getAuthToken() != null

    fun clearSession() {
        prefs.edit().clear().apply()
    }
}
