package com.example.studenttracker.data.model

import com.google.gson.annotations.SerializedName

data class LoginRequest(
    @SerializedName("username_or_email") val usernameOrEmail: String,
    val password: String
)

data class LoginResponseData(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("token_type") val tokenType: String,
    @SerializedName("user_id") val userId: Int,
    @SerializedName("role_id") val roleId: Int,
    val role: String,
    val name: String,
    val email: String
)

data class User(
    @SerializedName("user_id") val userId: Int,
    val username: String,
    val email: String,
    val role: String,
    val name: String,
    @SerializedName("is_active") val isActive: Boolean = true
)
