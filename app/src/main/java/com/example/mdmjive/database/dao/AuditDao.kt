package com.example.mdmjive.database.dao

import androidx.room.*
import com.example.mdmjive.database.entities.AuditRecord
import kotlinx.coroutines.flow.Flow

@Dao
interface AuditDao {
    @Query("SELECT * FROM audits ORDER BY timestamp DESC")
    fun getAllAudits(): Flow<List<AuditRecord>>

    @Insert
    suspend fun insertAudit(audit: AuditRecord)
    abstract fun <AuditRecord1> insert(audit: AuditRecord1)
}