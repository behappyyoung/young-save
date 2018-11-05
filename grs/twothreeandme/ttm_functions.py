import requests, json, yaml
from .models import ResponseLog, Chromosome, Accessions, GenomeSnpMap
from crsapi import functions
from crsapi import settings


def insert_map():
    filename = 'data/genome_snp_map.txt'
    try:
        with open(filename, "rU") as fp:
            content = fp.readlines()
        count = 0
        uni_count = 0
        prev_index = -1
        GenomeSnpMap.objects.all().delete()
        for line in content:
            count += 1
            line_l = line.strip().split('\t')
            position = line_l[3]
            ref = line_l[1]
            ttm_index = line_l[0]
            print(ttm_index, ref, position)
            if ttm_index != prev_index:
                snpmap = GenomeSnpMap(ttm_index=ttm_index, ref=ref, chromosome=line_l[2], position=position)
                snpmap.save()
                uni_count += 1
            else:
                prev = GenomeSnpMap.objects.get(ttm_index=ttm_index, chromosome=line_l[2], position=position)
                prev.ref = prev.ref + ', ' + ref
                prev.save()
            prev_index = ttm_index

            # try:
            #     prev = GenomeSnpMap.objects.get(position=position)
            #     prev.ref = prev.ref + ', ' + ref
            #     prev.save()
            # except GenomeSnpMap.DoesNotExist:
            #     snpmap = GenomeSnpMap(ttm_index=ttm_index, ref=ref, chromosome=line_l[2], position=position)
            #     snpmap.save()
            #     uni_count += 1
        fp.close()
        message = 'Data Updated : %s , unique : %s' % ( count, uni_count )
        status_code = 200
    except IOError as e:
        e_message = e.message if e.message else ','.join(map(str, e.args))
        message = 'Update Accession Error -   %s' % e_message
        status_code = 500

    return {'status_code': status_code, 'message': message}


def create_snp_map():
    # snp_maps1 = {}
    # snp_maps2 = {}
    # snp_maps3 = {}
    # snp_maps4 = {}
    # snp_maps5 = {}
    # snp_maps6 = {}
    snp_maps = {}
    snps = GenomeSnpMap.objects.all()
    for snp in snps:
        snp_maps[snp.ttm_index] = snp.id
    #         if snp.ttm_index < 300000:
    #             snp_maps1[snp.ttm_index] = snp.id
    #         elif snp.ttm_index < 600000:
    #             snp_maps2[snp.ttm_index] = snp.id
    #         elif snp.ttm_index < 900000:
    #             snp_maps3[snp.ttm_index] = snp.id
    #         elif snp.ttm_index < 1200000:
    #             snp_maps4[snp.ttm_index] = snp.id
    #         elif snp.ttm_index < 1500000:
    #             snp_maps5[snp.ttm_index] = snp.id
    #         else:
    #             snp_maps6[snp.ttm_index] = snp.id
    # snp_maps_list = [snp_maps1, snp_maps2, snp_maps3, snp_maps4, snp_maps5, snp_maps6]
    return snp_maps


def update_accessions(next_id=0, cid=1, offset=0):
    count = 0
    go_next = True
    # next_id = next_id
    try:
        while go_next:
            try:
                if next_id != 0:
                    current_chromsome = Chromosome.objects.get(id=next_id)
                else:
                    current_chromsome = Chromosome.objects.get(cid=cid, offset=offset)
            except Chromosome.DoesNotExist:
                raise functions.CustomError('no more')


            # data_list = Chromosome.objects.filter(cid=cid, offset=offset).order_by('id').values_list('data', flat=True)

            data_list = yaml.safe_load(current_chromsome.data)
            current_id = current_chromsome.id
            cid = current_chromsome.cid
            offset = current_chromsome.offset

            print('current id : %s, cid : %s, offset : %s, count : %s' % (current_id, cid, offset, count))
            next_id = int(current_id) + 1
            # print(data_list, type(data_list))
            for accession in data_list:
                # print(dlist, count, type(dlist))
                # accession_list = yaml.safe_load(dlist)
                first = True
                # print(len(accession_list))
                # for accession in accession_list:
                    # print(accession)
                accession_id = accession.get('accession_id')
                start_pos = accession.get('start')
                end_pos = accession.get('end')
                allele = accession.get('allele')
                platform_labels = accession.get('platform_labels')
                count += 1

                try:
                        if first:
                            c_accession = Accessions.objects.get(cid=cid, aid=accession_id, start_pos=start_pos, end_pos=end_pos)
                            c_accession.allele_1 = allele
                            platform_labels = platform_labels
                            first = False
                        else:
                            c_accession = Accessions.objects.get(cid=cid, aid=accession_id, start_pos=start_pos, end_pos=end_pos)
                            c_accession.platform_labels = platform_labels
                            c_accession.allele_2 = allele
                            first = True
                        c_accession.save()
                except Accessions.DoesNotExist:
                    try:
                        if first:
                            c_accession = Accessions(cid=cid, aid=accession_id, start_pos=start_pos, end_pos=end_pos,
                                                 allele_1=allele, platform_labels=platform_labels)
                            first = False
                            c_accession.save()
                        else:
                            raise functions.CustomError(
                                'Cannot find first allele for %s, start %s, end %s, allele %s, pl %s' % (
                                str(accession_id), str(start_pos), str(end_pos), str(allele), str(platform_labels) ))
                    except Exception as e:
                        e_message = e.message if e.message else ','.join(map(str, e.args))
                        data_str = 'accession : %s, start %s, end %s, allele %s, pl %s' % (
                            str(accession_id), str(start_pos), str(end_pos), str(allele), str(platform_labels))
                        message = ' %s : [%s]' % (e_message, data_str)
                        raise functions.CustomError(message)

                except Exception as e:
                    e_message = e.message if e.message else ','.join(map(str, e.args))
                    data_str = 'accession : %s, start %s, end %s, allele %s, pl %s' % (
                                str(accession_id), str(start_pos), str(end_pos), str(allele), str(platform_labels) )
                    message = ' %s : [%s]' % (e_message, data_str)
                    raise functions.CustomError(message)

                # if settings.LOCAL:
                #     print('accession_id : %s, allele : %s, start : %s, end : %s ' %
                #               (str(accession_id), str(allele), str(start_pos), str(end_pos)))



        message = 'total Accessions : %s ' % str(count)
        status_code = 200

    except Exception as e:
        e_message = e.message if e.message else ','.join(map(str, e.args))
        message = 'Update Accession Error -   %s' % (e_message)
        status_code = 505

    return {'status_code': status_code, 'message': message}


def process_request(current_url):
    data_r = requests.get(current_url)
    if data_r.status_code != 200:
        raise functions.CustomError(
            'Request Error - status code : %s, reason : %s' % (data_r.status_code, data_r.reason))
    json_re = yaml.safe_load(data_r.content)
    if not isinstance(json_re, dict):
        raise functions.CustomError('Cannot get Chromosome Data : %s' % current_url)
    else:
        c_data = json_re.get('data')
        links = json_re.get('links')

        url_s = current_url.split('&limit=')
        try:
            limit_offset = url_s[1].split('&offset=')
            limit = limit_offset[0]
            offset = limit_offset[1]
        except:
            offset = 0
            limit = 100

        cid = url_s[0].split('id=')[1]
        print(current_url, cid)
        try:
            chromosome = Chromosome.objects.get(url=current_url, cid=cid, offset=offset)
            chromosome.data = c_data
            chromosome.links = links
        except Chromosome.DoesNotExist:
            chromosome = Chromosome(url=current_url, cid=cid, offset=offset, data=c_data, links=links)
        chromosome.save()
        if links:
            have_next = True
            current_url = links.get('next')
            if not current_url:
                if cid == 22:
                    current_url = 'https://api.23andme.com/3/variant/?chromosome_id=X&limit=%s&offset=%s' % (limit, 0)
                elif cid == 'X':
                    current_url = 'https://api.23andme.com/3/variant/?chromosome_id=Y&limit=%s&offset=%s' % (limit, 0)
                elif cid == 'Y':
                    current_url = 'https://api.23andme.com/3/variant/?chromosome_id=MT&limit=%s&offset=%s' % (limit, 0)
                elif cid == 'MT':
                    have_next = False
                else:
                    current_url = 'https://api.23andme.com/3/variant/?chromosome_id=%s&limit=%s&offset=%s' % (
                    str(int(cid) + 1), limit, 0)
        else:
            have_next = False
    return {'have_next': have_next, 'current_url': current_url}


def update_chromosome(cid=1, offset='0', limit='1000'):
    current_url = 'https://api.23andme.com/3/variant/?chromosome_id=%s&limit=%s&offset=%s' % (cid, limit, offset)
    try:
        have_next = True
        done_url = []
        count = 0

        while have_next:
            count += 1
            print(current_url)
            f_re = process_request(current_url)
            have_next = f_re['have_next']
            done_url.append(current_url)
            current_url = str(f_re['current_url'])

        message = 'total : ' + str(count) + '   ' + ', '.join(done_url)
        status_code = 200

    except Exception as e:
        e_message = e.message if e.message else ','.join(map(str, e.args))
        message = '%s : Update Chromosome Error -   %s'%(current_url, e_message)
        status_code = 505

    return {'status_code': status_code, 'message': message}
