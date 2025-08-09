package com.example.mdmjive.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "devices")
data class DeviceInfo(
    @PrimaryKey val deviceId: String,
    val model: String,
    val manufacturer: String,
    val osVersion: String,
    val status: String,
    val lastSync: Long
)