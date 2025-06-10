package com.example.mdmjive.database.dao

import androidx.room.*
import com.example.mdmjive.database.entities.PolicyRecord
import kotlinx.coroutines.flow.Flow

@Dao
interface PolicyDao {
    @Query("SELECT * FROM policies ORDER BY appliedAt DESC")
    fun getAllPolicies(): Flow<List<PolicyRecord>>

    @Insert
    suspend fun insertPolicy(policy: PolicyRecord)
    abstract fun insert(policy: PolicyRecord)
}