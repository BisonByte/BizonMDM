package com.example.mdmjive.network.models

data class DeviceStatus(
    val deviceId: String,
    val status: String,
    val lastSync: Long = System.currentTimeMillis(),
    val rootAttempt: Boolean = false,
    val emulator: Boolean = false,
    val unknownSources: Boolean = false
)
