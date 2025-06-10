package com.example.mdmjive.database.dao

import androidx.room.*
import com.example.mdmjive.database.entities.LogEntry
import kotlinx.coroutines.flow.Flow

@Dao
interface LogDao {
    @Query("SELECT * FROM logs ORDER BY timestamp DESC")
    fun getAllLogs(): Flow<List<LogEntry>>

    @Insert
    suspend fun insertLog(log: LogEntry)

    @Query("DELETE FROM logs WHERE timestamp < :timestamp")
    suspend fun deleteOldLogs(timestamp: Long)
    abstract fun insert(logEntry: Any)
    abstract fun getLogsByDeviceId(deviceId: String)
}