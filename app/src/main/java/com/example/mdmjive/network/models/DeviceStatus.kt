package com.example.mdmjive.network.models

data class DeviceStatus(
    val deviceId: String,
    val status: String,
    val lastUpdate: Long = System.currentTimeMillis()
)
