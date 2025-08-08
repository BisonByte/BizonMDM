package com.example.mdmjive.receivers

import android.app.admin.DeviceAdminReceiver
import android.app.admin.DevicePolicyManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.os.Build
import android.content.pm.PackageManager
import com.example.mdmjive.MainActivity
import android.util.Log
import com.example.mdmjive.security.PolicyManager

class MDMDeviceAdminReceiver : DeviceAdminReceiver() {

    override fun onEnabled(context: Context, intent: Intent) {
        super.onEnabled(context, intent)
        Log.d("MDM", "Admin enabled")
        setupDeviceAdmin(context)
        hideLauncherIcon(context)
    }

    // Configura el dispositivo con las políticas de administración
    private fun setupDeviceAdmin(context: Context) {
        val dpm = context.getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
        val componentName = ComponentName(context, MDMDeviceAdminReceiver::class.java)

        // Verifica si la app es propietaria del dispositivo
        if (dpm.isDeviceOwnerApp(context.packageName)) {
            Log.d("MDM", "La app es propietaria del dispositivo. Aplicando políticas.")
            applyPolicies(context, dpm, componentName)
            startMDMService(context)
        } else {
            Log.e("MDM", "La app no es propietaria del dispositivo.")
        }
    }

    // Aplica las políticas de seguridad en el dispositivo
    private fun applyPolicies(context: Context, dpm: DevicePolicyManager, componentName: ComponentName) {
        try {
            // Aplicando las políticas
            dpm.apply {
                setLockTaskPackages(componentName, arrayOf(packageName))
                setCameraDisabled(componentName, true)
                setKeyguardDisabled(componentName, true)

                // Políticas adicionales de seguridad
                setPasswordQuality(componentName, DevicePolicyManager.PASSWORD_QUALITY_COMPLEX)
                setMaximumFailedPasswordsForWipe(componentName, 10)
                setMaximumTimeToLock(componentName, 30000L) // 30 segundos de bloqueo
                // Bloquear la desinstalación de la propia app
                setUninstallBlocked(componentName, packageName, true)
            }
            val policyManager = PolicyManager(context)
            policyManager.disableFactoryReset()
            policyManager.lockBrightness()
            policyManager.lockGPS()
            policyManager.lockDateTime()
            Log.d("MDM", "Políticas aplicadas correctamente.")
        } catch (e: Exception) {
            Log.e("MDM", "Error aplicando políticas: ${e.message}")
        }
    }

    // Inicia el servicio MDM
    private fun startMDMService(context: Context) {
        try {
            // Verifica si el sistema soporta el servicio de fondo
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(Intent(context, com.example.mdmjive.services.MDMService::class.java))
            } else {
                context.startService(Intent(context, com.example.mdmjive.services.MDMService::class.java))
            }
            Log.d("MDM", "Servicio MDM iniciado.")
        } catch (e: Exception) {
            Log.e("MDM", "Error iniciando el servicio MDM: ${e.message}")
        }
    }

    // Muestra un mensaje cuando el usuario intenta desactivar la administración
    override fun onDisableRequested(context: Context, intent: Intent): CharSequence? {
        Log.d("MDM", "Admin disable requested")
        return "Para salir utiliza el panel administrativo"
    }

    // Este método se llama cuando el dispositivo pierde la administración
    override fun onDisabled(context: Context, intent: Intent) {
        super.onDisabled(context, intent)
        Log.d("MDM", "Admin disabled - Intentando reactivar.")
        reactivateAdmin(context)
    }

    // Reactiva los permisos de administrador si es necesario
    private fun reactivateAdmin(context: Context) {
        val intent = Intent(DevicePolicyManager.ACTION_ADD_DEVICE_ADMIN).apply {
            putExtra(DevicePolicyManager.EXTRA_DEVICE_ADMIN,
                ComponentName(context, MDMDeviceAdminReceiver::class.java))
            putExtra(DevicePolicyManager.EXTRA_ADD_EXPLANATION,
                "Los permisos de administrador son necesarios para el funcionamiento del sistema")
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        context.startActivity(intent)
    }

    // Deshabilita el icono del lanzador para ocultar la aplicación
    private fun hideLauncherIcon(context: Context) {
        val packageManager = context.packageManager
        val component = ComponentName(context, MainActivity::class.java)
        packageManager.setComponentEnabledSetting(
            component,
            PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
            PackageManager.DONT_KILL_APP
        )
    }
}
