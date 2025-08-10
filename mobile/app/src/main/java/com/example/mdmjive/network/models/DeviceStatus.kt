package com.example.mdmjive.network.models

data class DeviceStatus(
    val deviceId: String,
    val status: String,
    val wipeDetected: Boolean = false,
    val bootloaderTampered: Boolean = false,
    val lastSync: Long = System.currentTimeMillis()
)
