package com.example.mdmjive.database.repository

import com.example.mdmjive.database.dao.AuditDao
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import com.example.mdmjive.database.dao.LogDao
import com.example.mdmjive.database.dao.DeviceDao
import com.example.mdmjive.database.dao.PolicyDao
import com.example.mdmjive.database.entities.DeviceInfo
import com.example.mdmjive.database.entities.LogEntry
import com.example.mdmjive.database.entities.PolicyRecord
import com.example.mdmjive.database.entities.AuditRecord

class LogRepository(
    private val logDao: LogDao,
    private val deviceDao: DeviceDao,
    private val policyDao: PolicyDao,
    private val auditDao: AuditDao
) {

    // Get logs for a specific device
    suspend fun getDeviceLogs(deviceId: String) = withContext(Dispatchers.IO) {
        logDao.getLogsByDeviceId(deviceId)
    }

    // Add a new log entry
    suspend fun addLog(type: String, message: String, severity: String, deviceId: String) {
        val logEntry = LogEntry(
            timestamp = System.currentTimeMillis(),
            type = type,
            message = message,
            severity = severity,
            deviceId = deviceId
        )
        logDao.insertLog(logEntry)
    }

    // Add device information
    suspend fun addDeviceInfo(deviceInfo: DeviceInfo) {
        deviceDao.insertDevice(deviceInfo)
    }

    // Add new policy
    suspend fun addPolicy(policy: PolicyRecord) {
        policyDao.insertPolicy(policy)
    }

    // Add audit record
    suspend fun addAudit(audit: AuditRecord) {
        auditDao.insertAudit(audit)
    }

    // Clean old logs based on a specified number of days
    suspend fun cleanOldLogs(daysToKeep: Int) {
        val cutoffTime = System.currentTimeMillis() - (daysToKeep * 24 * 60 * 60 * 1000)
        logDao.deleteOldLogs(cutoffTime)
    }
}
