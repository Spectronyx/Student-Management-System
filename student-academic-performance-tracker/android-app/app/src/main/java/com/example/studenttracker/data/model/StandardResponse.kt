package com.example.studenttracker.data.model

data class StandardResponse<T>(
    val success: Boolean,
    val message: String,
    val data: T? = null,
    val error: String? = null
)
