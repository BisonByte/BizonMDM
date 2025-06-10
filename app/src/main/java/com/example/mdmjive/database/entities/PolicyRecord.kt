package com.example.mdmjive.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "policies")
data class PolicyRecord(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val policyType: String,
    val value: String,
    val appliedAt: Long,
    val deviceId: String
)