/**
 * يعرض إشعارًا بسيطًا للمستخدم.
 * @param {string} message - الرسالة التي ستُعرض.
 * @param {string} type - نوع الإشعار ('success', 'error', 'info').
 */
function showNotification(message, type = 'info') {
    console.log(`Notification (${type}): ${message}`);

    // يمكنك هنا إضافة كود أكثر تعقيدًا لإنشاء عنصر HTML جميل للإشعار
    // على سبيل المثال، إنشاء div وتصميمه وإضافته إلى body
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    // إزالة الإشعار بعد فترة زمنية
    setTimeout(() => {
        notification.remove();
    }, 5000); // 5 ثوانٍ
}