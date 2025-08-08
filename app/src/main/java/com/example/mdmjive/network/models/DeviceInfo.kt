package com.example.mdmjive.network.models

data class DeviceInfo(
    val deviceId: String,
    val model: String,
    val manufacturer: String,
    val osVersion: String,
    val imei: String?,
    val serial: String?
)
