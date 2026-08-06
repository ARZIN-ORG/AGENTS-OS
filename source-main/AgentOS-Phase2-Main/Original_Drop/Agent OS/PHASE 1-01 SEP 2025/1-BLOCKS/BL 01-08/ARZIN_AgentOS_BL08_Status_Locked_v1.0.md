# وضعیت نهایی تا پایان BL-08 (Agent OS / AACP) — نسخه ۱.۰
شناسه: ARZIN-AOS-BL08-STATUS-v1.0  
دامنه: فاز ۱ (Private Cloud)  
هدف: جمع‌بندی «چه داریم / چه نداریم / چه باید بسازیم» با اعمال کامل موارد قفل‌شده و جلوگیری از دوباره‌کاری.

## ۱) موارد قفل‌شده و غیرقابل دور زدن در فاز ۱
این سند با فرض قطعی و اجرایی بودن قیود زیر نوشته شده است و هر جزء کد/سرویس که آن‌ها را enforce نکند باید Fail-fast/Reject کند.  
۱) معماری چندکاناله AACP الزامی است و bypass ممنوع است.  
۲) استقرار فاز ۱ روی Private Cloud الزامی است.  
۳) مدل اکوسیستمی-باز الزامی است، اما اتصال فقط از مسیر استاندارد و allowlist شده مجاز است.  
۴) اولویت ایجنت‌ها در فاز ۱ امنیتی (RedTeam/Resilience) و مدیریتی/Observability است.  
۵) در فاز ۱ و فاز ۲ هیچ ایجنتی «تصمیم اجرایی» نمی‌گیرد؛ خروجی ایجنت‌ها فقط Observe/Recommend است.  
۶) طراحی باید End-to-End امن، سریع، و مقاوم باشد و Single Point of Failure در مسیر حیاتی ممنوع است؛ اگر نیاز باشد چند کانال موازی اجباری است.  
۷) هر پیام و هر اقدام باید قابل حسابرسی باشد و مسیر audit مستقل از کد داخلی ایجنت‌ها نگهداری شود.

## ۲) تعریف مرجع: Agent OS = Control Plane + Data Plane
در فاز ۱ «Marketplace» سطح ارائه است و هسته سیستم‌عامل این دو صفحه است.  
Control Plane یعنی رجیستری، سیاست، نسخه، دامنه، کانال مجاز، SLA، سطح مشاهده/پیشنهاد، و قفل‌های اجازه/عدم اجازه.  
Data Plane یعنی جریان پیام AACP، Topicها، Payloadها، Observability و Audit.

## ۳) وضعیت واقعی تا پایان BL-08
این بخش صرفاً روی واقعیت فنی موجود متمرکز است و از نظر حاکمیتی و اجرایی، وضعیت را قفل می‌کند.

### ۳.۱ Data Plane (هسته پیام‌رسانی و اجرای گیت‌ها) — وضعیت: آماده برای تست E2E
وضعیت Data Plane در فاز ۱ قابل اتکا است، زیرا مسیر publish واحد، چندکاناله، و سخت‌گیرانه شده است و همه Rejectها به DLQ می‌روند و Audit قابل الحاق است.  
فایل‌های مرجع:  
`aacp_bl01_audit_envelope.py`  
`aacp_bl02_reject_dlq.py`  
`aacp_bl03_keystore_signature.py`  
`aacp_bl04_registry_policy.py`  
`aacp_bl05_channel_manager.py`  
`aacp_bl06_observability.py`  
`aacp_bl07_message_codec.py`  
`aacp_bl08_audit_sink.py`  
`aacp_bl06_08_interceptor_phase1.py`  
`aacp_bl05_08_kafka_manager_phase1.py`  
نسخه سازگار (پلاگین روی اسکیمای فعلی):  
`aacp_kafka_interceptor_PLUG_BL08.py`  
`aacp_kafka_manager_PLUG_BL08.py`

### ۳.۲ Control Plane (حاکمیت، سیاست، اجازه) — وضعیت: حداقلی درون‌کدی، سرویس‌محور نیست
در حال حاضر Registry/Policy/Permit به‌صورت Engine/Library و از طریق فایل‌های allowlist اجرا می‌شوند. این برای فاز ۱ «قابل شروع» است، اما برای میکروسرویسی قفل‌شده شما «کافی نیست» و باید سرویس مستقل داشته باشد.  
نتیجه قطعی: کمبود اصلی تا BL-08 «سرویس‌محور نبودن Control Plane» است، نه کمبود در Data Plane.

## ۴) ماتریس «چه داریم / چه نداریم / چه باید بسازیم» تا BL-08
| مولفه | وضعیت فعلی | مرجع پیاده‌سازی | نتیجه اجرایی فاز ۱ |
|---|---|---|---|
| Audit Envelope + Chain Hash + No-Execute | داریم (سخت‌گیر) | BL-01 + Interceptor | قابل تست و قابل اتکا |
| Reject → DLQ قطعی | داریم | BL-02 | هیچ خطایی silent نیست |
| Signature Verify با KeyStore/HSM-Abstraction | داریم | BL-03 | key_id ناشناخته یا امضای نامعتبر = Reject |
| Agent Registry (allowlist) | داریم، اما سرویس نداریم | BL-04 | برای فاز ۱ کافی، برای معماری میکروسرویسی کافی نیست |
| Policy Plane (allowlist) | داریم، اما سرویس نداریم | BL-04 | برای فاز ۱ کافی، برای معماری میکروسرویسی کافی نیست |
| Permit (Allow/Deny Gate) | داریم، اما embedded است | BL-06_08 Interceptor | باید سرویس مستقل شود تا separation-of-duty واقعی شود |
| Multi-Channel Routing | داریم | BL-05 | آماده تست در Private Cloud |
| Observability استاندارد | داریم | BL-06 | trace_id محور |
| Message Codec + payload_hash | داریم | BL-07 | کم‌هزینه و قابل اندازه‌گیری |
| Audit Sink (Kafka/File) + Fail-fast Guard | داریم | BL-08 | قابل فعال‌سازی عملیاتی |

## ۵) اقدام‌های لازم بعد از BL-08 (برای قفل میکروسرویس و جلوگیری از دوباره‌کاری)
برای اینکه «OS واقعی» شود و نه صرفاً Fabric، سه سرویس Control Plane باید ساخته شوند. این سرویس‌ها باید stateful، HA، و تحت حاکمیت تغییر باشند.  
سرویس ۱: Agent Registry Service  
سرویس ۲: Policy Plane Service  
سرویس ۳: Permit Service

این سه سرویس باید با Data Plane از طریق AACP و یا API داخلی امن در Private Cloud متصل شوند، اما نتیجه نهایی باید در Interceptor/SDK enforce شود تا bypass ممکن نباشد.

## ۶) نتیجه‌گیری قفل‌شده
تا پایان BL-08، Data Plane عملیاتی و سخت‌گیر است و برای تست E2E با Kafka و سها آماده است.  
خلأ قطعی و اصلی، سرویس‌محور نبودن Control Plane است.  
هر توسعه بعدی باید فقط در مسیر استاندارد publish و با enforce کامل قیود قفل‌شده انجام شود و هر مسیر موازی غیرمجاز باید Reject شود.
