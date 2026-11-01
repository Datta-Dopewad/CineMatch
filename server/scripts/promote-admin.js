import dotenv from 'dotenv';
import mongoose from 'mongoose';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
dotenv.config({path:path.resolve(here,'../../.env')});
const email=String(process.argv[2]||process.env.ADMIN_EMAIL||'').trim().toLowerCase();
if(!email){console.error('Provide the account email or set ADMIN_EMAIL in the root .env.');process.exit(2);}
if(!process.env.MONGODB_URI)throw Error('MONGODB_URI is required; refusing to connect to a local fallback.');
await mongoose.connect(process.env.MONGODB_URI);
const result=await mongoose.connection.collection('users').updateOne({email},{$set:{role:'admin'}});
await mongoose.disconnect();
if(!result.matchedCount){console.error(`No account found for ${email}. Register that account first.`);process.exit(1);}
console.log(`Admin access enabled for ${email}. Sign in again to refresh the session.`);
