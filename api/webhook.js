const admin = require('firebase-admin');
const LINE_ACCESS_TOKEN = 'JvIz6XX++UJ3HNUDcXTSRULrnFaHTpa8TX+mU5gQL4tti8UPSnQmkYdxkMtDlZ4aL0Zp9kXIDvDZRiVVq1lRG/4vGThJ47+FLYEvk2wBr3IQiu4xFo8Dip64rtrP3/EUtz74xwXvZi0w/lczdU6ovAdB04t89/1O/w1cDnyilFU=';

if (!admin.apps.length) {
  admin.initializeApp({
    credential: admin.credential.cert({
      projectId: "kousoku-6477e",
      clientEmail: "firebase-adminsdk-fbsvc@kousoku-6477e.iam.gserviceaccount.com",
      // 環境変数から読み込むのが安全ですが、一旦直接書く場合は \n の扱いに注意
      privateKey: "-----BEGIN PRIVATE KEY-----\nMIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQDGjg2m4tV86st0Ll5QYDl02+epvn6I5rsjtnVuokARGukH6PwM2oJY4jRRT9sBMROZdjoKRHOBII8mkLHu8yHPZWk5lFE8QFvSP3X7+py37KMPL47QvZ7tBzYuAZ2A+FGpk9RThz6iJNck0gzDUnGDYDQpxr6uj86KY7YfW8l2vfcdtCYIwPRiPqiiUm3u0ffiaijyBT6pnALMBK4vnugky4V/ntt4QlmnEtCiwPCHOeCObNp3CRHej/Kb+vsVv+ULsa+z+DzoreAKBbB/Ku6nPPUg8sKf2X205DWoPq+Gf/j2YDsbi6rbusG3bt4/jHZ41qca/gmOGeHma8UUZIT5AgMBAAECgf9WUHLe2CmVGnctxjexc52c3U9nUr1IHHTL2I9d+YvuPLVAJi3QK2qBc5y8zQEd2yh5VPLYTuxF8d1UOJr0u42nzoh2sujPs5RjjYOUYRmWDRVVeCOsz4oQwFX96fXYETxCSv0thJw0WCA/gW8j+d4eyvTtUBtlM8Ly9A95Yw1nuL8G9JHDdJeYzAB/PE1VUx2j3PW0c0vnxYzi14sZvNEabuAbsseem6ARgOA6SIzNGmiYJoIkoOD8nVBxpkYe7BDEe0H2f7Phdr3IN8/Pn+NFYtUrdH57Lg3I+2UX9/cWJndPsxU4Bn07Lld88K6AOWyzHfu8sqzvREfcgwrsloECgYEA74TQUqOs9kHIBiKrGqkh13kxDiG0xKJSAbDouwW62J2Q5ecAPU3C+Jc3TEZmcvlCV0+7iOgMZaSwDVAOz4one0QCT2YHz5gDSyKavRje5CNZr2xWycY3jcscHRNyMhz4x2OszpZEAclQPAtDW+M6mdDRE4s8DHuSB6MFZSWwtIECgYEA1DemTqJxRprJWDlsDb29MhUIxJg83uADlVoqhteuxJiLUmCarMl0RuPhS8vEFGtsDukE+DhsE30cuYsQr9fOPhzKHBW9sFbllaajp9v18joMEI6N6xHdnYgcHo7jCG5GmcoHMSZN+GsmbpSOO7+Wjk6jQOjkLpmFUcYO/sC1NHkCgYA8Xlc7XPGNJ8tIcJh7ocFb07nfe/NZ1CejMXmXGbycOCp7J5vR17WaflJ7sQrFU7m60+fKe+IUBEwzLshs2r9UvDFw3aB+XCwIVfJ2Urxq99X09vNw67q4zEaLtYkExHSXnLHDZ/BAGwNT/uq9UCpG9nCb4m4CH2sQ7a/AbJ17AQKBgEKp1JFBEApY10TijOHoJ4WS+/UdyYlNn3KMJ23CVQEm1iUjeZMrmV4neX9g3BB6CjDI3CnJN5ILrDlQyQYj6YKzcn3OCo9ZTLds6F3zh9f2ihGtZkFglFhHCGZFBmaAlab7wrSazsVpi2ITQnbcYUQEyd27CurkiO++Irm9+W4pAoGBAOD1QCYenZphzOoUj1IGJ/p05VnZKxaHnXn7ST0mAFBYaDedM/gp3BPzw0B1JjzjH4iq24cLz9g6+0F6OIgkjrsIbQzwbdyOKQVo03t+VUdNv6ySyGv0Fz2UYopgeIoe1ldtgeABTG640lqGKFdpopFGdzB7uElR2AX7JXMHcbG/\n-----END PRIVATE KEY-----\n",
    })
  });
}

const db = admin.firestore();
module.exports = async (req, res) => {
  // LINEからの検証やPOST以外は無視
  if (req.method !== 'POST') {
    return res.status(200).send('OK');
  }

  try {
    const events = req.body.events;
    if (!events || events.length === 0) {
      return res.status(200).send('No events');
    }

    const event = events[0];

    if (event.type === 'message' || event.type === 'follow') {
      const replyToken = event.replyToken;

      // Firestoreから取得
      const doc = await db.collection('latest_broadcast').doc('text').get();
      
      let messageText = "データが見つかりませんでした";
      
      if (doc.exists) {
        const data = doc.data(); // ここで data に代入
        messageText = data["0"] || "内容なし"; // data を参照
      }

      // LINEに返信
      await fetch('https://api.line.me/v2/bot/message/reply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${LINE_ACCESS_TOKEN}`
        },
        body: JSON.stringify({
          replyToken: replyToken,
          messages: [{ type: 'text', text: messageText }]
        })
      });
    }

    res.status(200).send('OK');
  } catch (error) {
    console.error("Error Detail:", error);
    // 401エラーを回避するため、エラー時も200を返しつつログを出す
    res.status(200).send('Internal Error But OK');
  }
};


