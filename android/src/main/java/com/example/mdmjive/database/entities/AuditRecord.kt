package com.example.mdmjive.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "audits")
data class AuditRecord(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val action: String,
    val timestamp: Long,
    val details: String,
    val deviceId: String
)