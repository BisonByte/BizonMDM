package com.example.mdmjive.monitoring

import android.util.Log
import com.example.mdmjive.database.LogDatabase
import com.example.mdmjive.database.entities.LogEntry
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.util.Date

class LogManager(private val logDatabase: LogDatabase) {

    // Función para registrar un evento en los logs
    fun logEvent(event: MDMEvent) {
        val entry = LogEntry(
            timestamp = Date(),
            type = event.type,
            message = event.message,
            details = event.details
        )
        saveLog(entry)
    }

    // Función para registrar errores
    fun logError(error: Throwable) {
        val entry = LogEntry(
            timestamp = Date(),
            type = "ERROR",
            message = error.message ?: "Unknown error",
            details = error.stackTraceToString()
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
                // Simulación de la subida de logs al servidor
                val logsToUpload = logDatabase.logDao().getAllLogs()
                // Aquí implementarías la lógica para subir los logs a tu servidor
                // Por ejemplo, usando Retrofit
                // retrofitService.uploadLogs(logsToUpload)

                // Si la subida fue exitosa, puedes limpiar los logs de la base de datos
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
    val details: String? = null
)
