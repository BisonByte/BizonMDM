package com.example.mdmjive.monitoring

import android.util.Log
import com.example.mdmjive.database.LogDatabase
import com.example.mdmjive.database.entities.LogEntry
import com.example.mdmjive.network.ApiServiceFactory
import com.example.mdmjive.network.models.LogEntryPayload
import com.example.mdmjive.network.models.LogPayload
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class LogManager(private val logDatabase: LogDatabase) {

    private val apiService = ApiServiceFactory.create("https://example.com/")

    // Función para registrar un evento en los logs
    fun logEvent(event: MDMEvent, deviceId: String = "unknown") {
        val entry = LogEntry(
            timestamp = System.currentTimeMillis(),
            type = event.type,
            message = event.message,
            severity = event.severity,
            deviceId = deviceId
        )
        saveLog(entry)
    }

    // Función para registrar errores
    fun logError(error: Throwable, deviceId: String = "unknown") {
        val entry = LogEntry(
            timestamp = System.currentTimeMillis(),
            type = "ERROR",
            message = error.message ?: "Unknown error",
            severity = "HIGH",
            deviceId = deviceId
        )
        saveLog(entry)
    }

    // Guardar log en la base de datos o en almacenamiento persistente
    private fun saveLog(entry: LogEntry) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                // Insertar el log en la base de datos (o archivo)
                logDatabase.logDao().insertLog(entry)
            } catch (e: Exception) {
                Log.e("LogManager", "Error guardando log: ${e.message}")
            }
        }
    }

    // Subir logs al servidor
    fun uploadLogs() {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val logsToUpload = logDatabase.logDao().getAllLogsOnce()
                if (logsToUpload.isEmpty()) return@launch

                val deviceId = logsToUpload.first().deviceId
                val payload = LogPayload(
                    deviceId = deviceId,
                    logs = logsToUpload.map {
                        LogEntryPayload(
                            timestamp = it.timestamp,
                            type = it.type,
                            message = it.message,
                            severity = it.severity
                        )
                    }
                )

                apiService.uploadLogs(payload)
                logDatabase.logDao().clearLogs()
            } catch (e: Exception) {
                Log.e("LogManager", "Error subiendo logs: ${e.message}")
            }
        }
    }

    // Limpiar los logs de la base de datos
    fun clearLogs() {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                logDatabase.logDao().clearLogs()
            } catch (e: Exception) {
                Log.e("LogManager", "Error limpiando logs: ${e.message}")
            }
        }
    }
}

data class MDMEvent(
    val type: String,
    val message: String,
    val severity: String = "INFO",
    val details: String? = null
)
