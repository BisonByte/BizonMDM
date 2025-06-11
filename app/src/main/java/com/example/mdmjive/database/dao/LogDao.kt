package com.example.mdmjive.database.dao

import androidx.room.*
import com.example.mdmjive.database.entities.LogEntry
import kotlinx.coroutines.flow.Flow

@Dao
interface LogDao {
    @Query("SELECT * FROM logs ORDER BY timestamp DESC")
    fun getAllLogs(): Flow<List<LogEntry>>

    @Query("SELECT * FROM logs ORDER BY timestamp DESC")
    suspend fun getAllLogsOnce(): List<LogEntry>

    @Query("SELECT * FROM logs WHERE deviceId = :deviceId ORDER BY timestamp DESC")
    fun getLogsByDeviceId(deviceId: String): Flow<List<LogEntry>>

    @Insert
    suspend fun insertLog(log: LogEntry)

    @Query("DELETE FROM logs WHERE timestamp < :timestamp")
    suspend fun deleteOldLogs(timestamp: Long)

    @Query("DELETE FROM logs")
    suspend fun clearLogs()
}