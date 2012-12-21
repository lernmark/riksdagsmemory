package net.lernmark.riksdagens;

import java.io.IOException;
import javax.servlet.http.*;

import java.net.MalformedURLException;
import java.net.URL;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;

@SuppressWarnings("serial")
public class RiksdagensServlet extends HttpServlet {
	public void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
		String urlParameter = "http://data.riksdagen.se/personlista/?valkrets=Stockholms+kommun&utformat=json";
		String cType = req.getParameter("ctype");
		String cTime = req.getParameter("ctime");
		String jsoncallback = req.getParameter("jsoncallback");
		String cControl = req.getParameter("ccontrol");		
		
		if (urlParameter != null) {
			try {
				
				String prot = urlParameter.substring(0, 4);
				if (!prot.equalsIgnoreCase("http")) {
					urlParameter = "http://" + req.getServerName() + urlParameter;
				}
				
				URL url = new URL(urlParameter);

	            BufferedReader reader = new BufferedReader(new InputStreamReader(url.openStream(),"UTF-8"));

	            if (cControl == null) {
	            	cControl = "private";
	            }
	            
	            if (cTime != null) {
		            resp.setHeader("Cache-Control", cControl + ", max-age=" + cTime);	    			
	    		}

	            resp.setCharacterEncoding("utf-8");

	            if (cType == null || cType.equals("")) {
	            	resp.setContentType("application/json; charset=UTF-8"); 
	            } else {
	            	resp.setContentType(cType + "; charset=UTF-8");
	            }				
				
				if (jsoncallback != null) {
					resp.getWriter().println(jsoncallback + "(");
				}	            
	            
				String line;
				while ((line = reader.readLine()) != null) {
					resp.getWriter().println(line);
				}

				if (jsoncallback != null) {
					resp.getWriter().println(")");
				}
				
				reader.close();

			} catch (MalformedURLException e) {
				System.err.println(e);
			} catch (IOException e) {
				System.err.println(e);
			}
		}
	
	}
}
