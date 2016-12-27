    $(function () {
                
 
				var father=[];
				var mother=[];
                var sibling=[];
				var siblings=[];
				var son =[];
                var daughter=[];
                var tempHtml ='';
				for(var i=0; i< family.length;i++){
					if(family[i].relationship == 'Father'){
						father.push(family[i]);
                        father[0].relationship = '/sample/'+father[0].id+'/';  
                        father[0].label = "Father";
                        $('.father').css('display', 'block');
                        $('.father .patient').html(father[0].relative);
					}
					else if(family[i].relationship == 'Mother'){
						mother.push(family[i]);
                        $('.mother').css('display', 'block');
                        mother[0].url = '/sample/'+mother[0].id+'/';  
                        $('.mother .patient').html(mother[0].relative);  

                    }else if(family[i].relationship == 'Sibling'){
                        sibling.push(family[i]);
					}else if(family[i].relationship == 'Son'){
                        son.push(family[i]);
                        son[0].relationship = '/sample/'+son[0].id+'/';  
                        son[0].label = "Son";
                       
                       
                    }else if(family[i].relationship == 'Daughter'){
                        daughter.push(family[i]);
                        daughter[0].relationship = '/sample/'+daughter[0].id+'/';  
                        daughter[0].label = "Daughter";
                    
                    }else if(family[i].relationship == 'Patient'||family[i].relationship == 'Self'){
                        proband={'mrn': family[i].mrn};
                        
                    }
				}

                $('.proband .patient').html(proband.mrn);

                if(daughter.length >0 ){
                        $('.daughter').css('display', 'block');
                        tempHtml ='';
                        for(var i=0; i<daughter.length;i++){
                            tempHtml += daughter[i].relative + '<br />';
                        }   
                        $('.daughter .patient').html(tempHtml);
                }

                if(son.length >0 ){
                        $('.son').css('display', 'block');
                        tempHtml ='';
                        for(var i=0; i<son.length;i++){
                            tempHtml += son[i].mrn + '<br />';
                        }   
                        $('.son .patient').html(tempHtml);
                }

                if(sibling.length  <=0){
                    $('.sibling').css('display', 'none');
                }else{
                    $('.sibling1 .patient').html(sibling[0].relative);
                    if(typeof sibling[1] == 'undefined'  ){
                         $('.sibling2').css('display', 'none');
                    }else{
                        $('.sibling2 .patient').html(sibling[1].relative);
                    }
                    if(typeof sibling[2] == 'undefined'  ){
                         $('.sibling3').css('display', 'none');
                    }else{
                        $('.sibling3 .patient').html(sibling[2].relative);
                        $('.relation-tree').css('margin-left', '0');
                    }
                }




  			
if(window.location.hostname =='gims-dev.shc.org'){
                console.log('family', family,  father, 'm', mother,'proband', proband, 'sibling', sibling);

 }
            if( father.length ==0 && mother.length == 0){
                $('.relation-tree').css({'top': '-150px'});
                if( son.length ==0 && daughter.length == 0){
                    $('.relation-tree').css({'height': '100px'});        
                }else{
                    $('.relation-tree').css({'height': '250px'});
                }
            }else {
                if( son.length ==0 && daughter.length == 0){
                    $('.relation-tree').css({'height': '250px'});        
                }else{
                    $('.relation-tree').css({'height': '500px'});
                }
            }



});
