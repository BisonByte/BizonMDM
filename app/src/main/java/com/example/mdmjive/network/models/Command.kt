package com.example.mdmjive.network.models

data class Command(
    val action: String,
    val packageName: String? = null,
    val message: String? = null
)
