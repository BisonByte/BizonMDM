package com.example.mdmjive.network.models

data class LogEntryPayload(
    val timestamp: Long,
    val type: String,
    val message: String,
    val severity: String
)

data class LogPayload(
    val deviceId: String,
    val logs: List<LogEntryPayload>
)
